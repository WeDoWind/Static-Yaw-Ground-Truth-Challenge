print('###########################\n'
      'IMPORTING PYTHON MODULES\n'
      '###########################')

import numpy as np
import pandas as pd
import os
from bokeh.plotting import show
from testChallenge4WeDoWind.utils.yaw_misalignment import StaticYawMisalignment
from testChallenge4WeDoWind.utils import plot, filters
from WindUFSM.OpenOA.openoa.plant import PlantData
from testChallenge4WeDoWind.utils.OpenOA_utils import generate_lhb_reanalysis_data, generate_lhb_curtail_data, generate_grid_data

print('\n#######################\n'
      'SETTING CODE PARAMETERS\n'
      '#######################')

AVENTA_TURBINE_PARAMETERS = {
    'HUB_HEGHT': 18,
    'ROTOR_DIAMENTER': 12.8,
    'RATED_POWER': 6.5
}

DATASET_AVENTA_PARAMETERS = {
    'SCADA_INPUT_FOLDER_PATH': './data/',
    'RESOLUTION': ['_1s', '_30s', '_1min', '_2min', '_3min', '_10min'],
    'RENAME_COLS_OPENOA_TRAIN': {'T1 # Date and time': 'Date_time',
                              'Turbine name': 'Wind_turbine_name',
                              'T1 Mean Blade Angle (°)': 'Ba_avg',
                              'T1 Power (kW)': 'P_avg',
                              'T1 Vane position 1+2 (°)': 'Va_avg',
                              'T1 Yaw Direction': 'Ya_avg',
                              'T1 Wind Direction': 'Wa_avg',
                              'T1 Wind Speed (m/s)': 'Ws_avg'},

    'COLS_SCADA_AVENTA_TRAIN': ['T1 # Date and time',
                             'Turbine name',  # calculated
                             'T1 Mean Blade Angle (°)',
                             'T1 Power (kW)',
                             'T1 Vane position 1+2 (°)',
                             'T1 Yaw Direction',  # calculated
                             'T1 Wind Direction',  # calculated
                             'T1 Wind Speed (m/s)'],
    'RENAME_COLS_OPENOA_TEST': {'Turbine name': 'Wind_turbine_name',
                                   'segment_time': 'Date_time',
                                   'blade_pitch_deg': 'Ba_avg',
                                   'power_output': 'P_avg',
                                   'relative_wind_direction': 'Va_avg',
                                   'T1 Yaw Direction': 'Ya_avg',
                                   'T1 Wind Direction': 'Wa_avg',
                                   'wind_speed': 'Ws_avg'},
    'COLS_SCADA_AVENTA_TEST': ['segment_time',
                                  'row_id',
                                  'wind_speed',
                                  'power_output',
                                  'relative_wind_direction',
                                  'blade_pitch_deg',
                                  'Turbine name',  # calculated
                                  'T1 Yaw Direction',  # calculated
                                  'T1 Wind Direction'],  # calculated
    'OFFSET': ['0', '4', '6'],
    'PITCH_THRESHOLD': 23,
    'POWER_BIN_MAD_THRESHOLD': 7,
    'WS_BINS': [3.0, 4.0, 5.0, 6.0],
    'WS_BINS_WIDTH': 1,
    'VANE_BINS_WIDTH': 1,
    'NUM_POWER_BINS': 25,
    'MIN_VANE_BIN_COUNT': 1,
    'MAX_ABS_VANE_ANGLE': 50,
    'NUM_SIM_NO_UQ': 1,
    'NUM_SIM_UQ': 100,
    'MIN_POWER_FILTER': 0.01,
    'MAX_POWER_FILTER': 0.95,
    'POWER_COEFF': False
}

GENERAL_PARAMETERS = {
    'RESULTS_VERSION': '2',
    'POWER_BIN_MAD_THRESHOLD': 7.0,
    'PITCH_THRESHOLD': 15.0,
    'APPLY_FILTERS': True,
    'PLOT_MAP': False,
    'PLOT_PITCH': False,
    'MODE': 'TEST', #'TEST', 'TRAIN', 'V1'
    'OUTPUT_DIR_AVENTA': './results',
    'ALGORITHM': 'AVENTA',
    'SHIFT': ['ALL DAY'], #'DAY', 'NIGHT', 'ALL DAY'
    'DPI': 150
}


####################################
#       DEFINING FUNCTIONS
####################################

def select_day_night_time(df: pd.DataFrame) -> pd.DataFrame:
    daylight_time = (8, 18)

    df['Hour'] = df['T1 # Date and time'].dt.hour

    if shift == 'DAY':
        print('Filtering DAY SHIFT data')
        print(f'Number of rows before DAY SHIFT filter: {len(df)}')
        df = df[(df['Hour'] >= daylight_time[0]) & (df['Hour'] <= daylight_time[1])].copy()
        print(f'Number of rows after DAY SHIFT filter: {len(df)}')

    else:
        print('Filtering NIGHT SHIFT data')
        print(f'Number of rows before NIGHT SHIFT filter: {len(df)}')
        df = df[~((df['Hour'] >= daylight_time[0]) & (df['Hour'] <= daylight_time[1]))].copy()
        print(f'Number of rows after NIGHT SHIFT filter: {len(df)}')

    return df


def collect_and_process_scada_data():
    print('\nCollecting SCADA data...')
    mode = ''
    file_name = ''

    if GENERAL_PARAMETERS['MODE'] == 'V1':
        file_name = f'OST_Aventa{res}.parquet'
        mode = 'TRAIN'
    elif GENERAL_PARAMETERS['MODE'] == 'TRAIN':
        file_name = f'train_OST_Aventa{res}.parquet'
        mode = 'TRAIN'
    elif GENERAL_PARAMETERS['MODE'] == 'TEST':
        file_name = f'test.parquet'
        mode = 'TEST'
    df = pd.read_parquet(f'{DATASET_AVENTA_PARAMETERS["SCADA_INPUT_FOLDER_PATH"]}{file_name}')

    # Generating calculated columns
    df['Turbine name'] = 'T1'
    df['T1 Yaw Direction'] = 0
    df['T1 Wind Direction'] = 0

    # Filtering shift
    if shift in ['DAY', 'NIGHT']:
        df = select_day_night_time(df)

    # Generating a virtual power of turbine
    df['power_output'] = df['power_output'] * 1000

    # Selecting data based on the offset
    if offset == '0':
        print('COLLECTING DATA WITH 0º OFFSET')
        df = df.loc[df['T1 Yaw Offset'] == 0.0].copy()

    elif offset == '4':
        print('COLLECTING DATA WITH 4º OFFSET')
        df = df.loc[df['T1 Yaw Offset'] == 4.0].copy()

    elif offset == '6':
        print('COLLECTING DATA WITH 6º OFFSET')
        df = df.loc[df['T1 Yaw Offset'] == 6.0].copy()

    else:
        print('COLLECTING DATA WITH ALL OR UNKNOWN OFFSETS')

    # Filtering and renaming columns based on the mode
    df = df[DATASET_AVENTA_PARAMETERS[f'COLS_SCADA_AVENTA_{mode}']].copy()
    df.rename(columns=DATASET_AVENTA_PARAMETERS[f'RENAME_COLS_OPENOA_{mode}'], inplace=True)

    print(f'Scada Data Columns: {df.columns}')
    print(f'Scada Data Index: {df.index}')
    return df


def collect_and_process_asset_data(df_scada: pd.DataFrame):
    print('\nCollecting ASSET data...')
    df_dict = {}

    df_dict['Wind_turbine_name'] = np.concatenate([df_scada['Wind_turbine_name'].unique(), np.array(
        ['T2'])])  # Creating a new turbine T2 for testing purposes
    df_dict['Rated_power'] = AVENTA_TURBINE_PARAMETERS['RATED_POWER']
    df_dict['Hub_height_m'] = AVENTA_TURBINE_PARAMETERS['HUB_HEGHT']
    df_dict['Rotor_diameter_m'] = AVENTA_TURBINE_PARAMETERS['ROTOR_DIAMENTER']
    df_dict['type'] = 'turbine'

    df_dict['elevation_m'] = 490
    df_dict['Longitude'] = 8.682139
    df_dict['Latitude'] = 47.520056

    return pd.DataFrame(df_dict)


def define_unused_df():
    print('\nCollecting Unused data...')
    df_meter = generate_grid_data()
    df_curtail = generate_lhb_curtail_data()
    df_reanalysis = generate_lhb_reanalysis_data()

    return df_meter, df_curtail, df_reanalysis


def collect_and_process_input_data():
    print('\nCollecting input data...')
    df_scada = collect_and_process_scada_data()
    df_asset = collect_and_process_asset_data(df_scada)
    print(f'{df_asset}')
    df_meter, df_curtail, df_reanalysis = define_unused_df()

    return PlantData(analysis_type="MonteCarloAEP",
                     metadata='./data/aventa_plant_meta.yml',
                     scada=df_scada,
                     meter=df_meter,
                     curtail=df_curtail,
                     asset=df_asset,
                     reanalysis=df_reanalysis)


def plot_map(project):
    print('\nPlotting Map...')
    show(plot.plot_windfarm(project.asset, tile_name="OpenMap", plot_width=600, plot_height=600))


def filter_data(project):
    pitch_threshold = GENERAL_PARAMETERS['PITCH_THRESHOLD']
    power_bin_mad_thresh = GENERAL_PARAMETERS['POWER_BIN_MAD_THRESHOLD']

    df_t= project.scada.loc[(slice(None), 'T1'), :]
    df_sub = df_t.loc[df_t["WROT_BlPthAngVal"] <= pitch_threshold]

    # Apply power bin filter
    turb_capac = project.asset.loc['T1', "rated_power"]
    flag_bin = filters.bin_filter(
        bin_col=df_sub["WTUR_W"],
        value_col=df_sub["WMET_HorWdSpd"],
        bin_width=0.04 * 0.94 * turb_capac,
        threshold=power_bin_mad_thresh,
        center_type="median",
        bin_min=0.01 * turb_capac,
        bin_max=0.95 * turb_capac,
        threshold_type="mad",
        direction="all",
    )
    outliers_df = flag_bin[flag_bin.eq(True)].index.to_frame(index=False).copy()
    timestamp_filtered = outliers_df['Date_time']
    time_mask = ~df_sub.index.get_level_values('Date_time').isin(timestamp_filtered)
    df_power = df_sub[time_mask].copy()

    project.scada = df_power.copy()
    return project


def plot_pitch(project):
    print('\nPlotting Pitch Angle by Turbine...')

    plot.plot_by_id(
        project.scada,
        id_col="asset_id",
        x_axis="WMET_HorWdSpd",
        y_axis="WROT_BlPthAngVal",
        xlabel="Wind Speed (m/s)",
        ylabel="Blade Pitch Angle (deg.)",
        xlim=(0, 15),
        ylim=(10, 50),
        max_cols=2,
        figure_kwargs={"figsize": (12, 8)},
    )


def plot_power_curve_filter_results(df_sub, flag_bin):
    plot.plot_power_curve(
        wind_speed=df_sub["WMET_HorWdSpd"],
        power=df_sub["WTUR_W"],
        flag=flag_bin,
        flag_labels=("Outliers", "Power Curve"),
        legend=True
    )


def calc_ym_no_uq(project):
    print('\nCalculating Yaw Misalignment Without Uncertainty Quantification...')
    dict_ym_no_uq = {'AEG': [], 'YM (deg)': []}
    ws_bins_set_on_dict = False

    for t in project.turbine_ids:
        print(f'\nAEG: {t}')

        try:
            yaw_mis = StaticYawMisalignment(
                plant=project,
                turbine_ids=[t],
                UQ=False,
                ws_bins=DATASET_AVENTA_PARAMETERS['WS_BINS']
            )

            if not ws_bins_set_on_dict:
                for k, ws in enumerate(yaw_mis.ws_bins):
                    dict_ym_no_uq[f'YM at {ws} m/s (deg)'] = []
                ws_bins_set_on_dict = True

            yaw_mis.run(num_sim=DATASET_AVENTA_PARAMETERS['NUM_SIM_NO_UQ'],
                        ws_bins=DATASET_AVENTA_PARAMETERS['WS_BINS'],
                        ws_bin_width=DATASET_AVENTA_PARAMETERS['WS_BINS_WIDTH'],
                        vane_bin_width=DATASET_AVENTA_PARAMETERS['VANE_BINS_WIDTH'],
                        min_vane_bin_count=DATASET_AVENTA_PARAMETERS['MIN_VANE_BIN_COUNT'],
                        max_abs_vane_angle=DATASET_AVENTA_PARAMETERS['MAX_ABS_VANE_ANGLE'],
                        pitch_thresh=DATASET_AVENTA_PARAMETERS['PITCH_THRESHOLD'],
                        num_power_bins=DATASET_AVENTA_PARAMETERS['NUM_POWER_BINS'],
                        power_bin_mad_thresh=DATASET_AVENTA_PARAMETERS['POWER_BIN_MAD_THRESHOLD'],
                        min_power_filter=DATASET_AVENTA_PARAMETERS['MIN_POWER_FILTER'],
                        max_power_filter=DATASET_AVENTA_PARAMETERS['MAX_POWER_FILTER'],
                        use_power_coeff=DATASET_AVENTA_PARAMETERS['POWER_COEFF']
                        )

            fig_yaw_mis = yaw_mis.plot_yaw_misalignment_by_turbine(return_fig=True)['T1']
            print(fig_yaw_mis)
            fig_yaw_mis[0].savefig(f'{GENERAL_PARAMETERS["OUTPUT_DIR_AVENTA"]}/sym{shift}_{offset}_{res}.png',
                                   dpi=150)

            for i, t in enumerate(yaw_mis.turbine_ids):
                # print(f"Overall yaw misalignment for Turbine {t}: {np.round(yaw_mis.yaw_misalignment[i], 1)} degrees")
                dict_ym_no_uq['AEG'].append(t)
                dict_ym_no_uq['YM (deg)'].append(np.round(yaw_mis.yaw_misalignment[i], 1))

                for k, ws in enumerate(yaw_mis.ws_bins):
                    # print(f'WS | YM : {ws} | {yaw_mis.yaw_misalignment_ws[i, k]}')
                    dict_ym_no_uq[f'YM at {ws} m/s (deg)'].append(np.round(yaw_mis.yaw_misalignment_ws[i, k]))

            # axes_dict = yaw_mis.plot_yaw_misalignment_by_turbine(return_fig=True)
            # print(f'Axes Dict: {axes_dict}')
        except Exception as e:
            print(f'Error on calculating Yaw Misalignment for Turbine {t}\n'
                  f'Error Message: {e}')

    return pd.DataFrame(dict_ym_no_uq)


def save_df(df, folder, row_id):
    print('\nSaving DataFrame...')

    path = os.path.join(GENERAL_PARAMETERS['OUTPUT_DIR_AVENTA'], folder)

    result_filename = f'YM_noUQ_AVENTA_{res}'
    result_test_filename = f'Results_2_{GENERAL_PARAMETERS['RESULTS_VERSION']}'

    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, f"{result_filename}.csv")
    df.to_csv(full_path)
    print(f"DataFrame Saved: {full_path}")

    df_test = pd.DataFrame()
    df_test['row_id'] = row_id# np.arange(0, 1064641, 1)
    df_test['yaw_offset'] = df['YM (deg)'].iloc[0]
    df_test = df_test[['row_id', 'yaw_offset']].copy()
    full_test_path = os.path.join(path, f"{result_test_filename}.csv")
    df_test.to_csv(full_test_path, index=False)
    print(f'Length of Result DataFrame: {len(df_test)}')
    print(f"Test DataFrame Saved: {full_test_path}")

def adjust_datetime(project):
    print('\nGenerating Generic DateTime...')
    print(project.scada.index)
    project.scada.index.names = ['Date_time', 'Wind_turbine_name']
    project.scada.reset_index(inplace=True)
    project.scada['Date_time'] = pd.date_range(start='2023-01-01 00:00:00', periods=len(project.scada), freq='10min')
    project.scada = project.scada.set_index(['Date_time', 'Wind_turbine_name'])
    print(project.scada.index)
    return project

#################
# MAIN FUNCTION
#################

def main():
    print('\n#####################\n'
          'RUNNING MAIN FUNCTION\n'
          '#####################')

    project = collect_and_process_input_data()
    print('\n######################\n'
          'Project Data Collected\n'
          '######################')

    project.analysis_type.append("StaticYawMisalignment")
    project.validate()
    print('\n#################\n'
          'Project Validated\n'
          '#################')

    project = adjust_datetime(project)
    row_id_tag = project.scada['row_id']


    if GENERAL_PARAMETERS['APPLY_FILTERS']:
        print('\n\nApplying Filters')
        print(len(project.scada))
        project = filter_data(project)
        print(len(project.scada))

    if GENERAL_PARAMETERS['PLOT_MAP']:
        plot_map(project)

    if GENERAL_PARAMETERS['PLOT_PITCH']:
        plot_pitch(project)

    df_ym_no_uq = calc_ym_no_uq(project)
    print('\n########################\n'
          'YM Without UQ Calculated\n'
          '########################')
    save_df(df_ym_no_uq, 'YawMisalignment_Without_UQ', row_id_tag)


if __name__ == '__main__':
    if GENERAL_PARAMETERS['MODE'] == 'TEST':
        shift = 'TEST'
        res = 'TEST'
        offset = 'TEST'
        GENERAL_PARAMETERS['OUTPUT_DIR_AVENTA'] = f'./results/test_dataset'
        main()


    elif GENERAL_PARAMETERS['MODE'] in ['TRAIN', 'V1']:
        for res in DATASET_AVENTA_PARAMETERS['RESOLUTION']:
            print(f'\n\n{"#" * 30}\n'
                  f'ANALYSING RESOLUTION: {res}\n'
                  f'{"#" * 30}\n')
            for shift in GENERAL_PARAMETERS['SHIFT']:
                print(f'\n\n{"#" * 30}\n'
                      f'ANALYSING SHIFT: {shift}\n'
                      f'{"#" * 30}\n')
                for offset in DATASET_AVENTA_PARAMETERS['OFFSET']:
                    print(f'\n\n{"#" * 30}\n'
                          f'ANALYSING YAW MISALIGNMENT OFFSET: {offset}\n'
                          f'{"#" * 30}\n')
                    GENERAL_PARAMETERS['OUTPUT_DIR_AVENTA'] = f'./results/{shift}/{offset}'
                    try:
                        main()
                    except:
                        print(f'ERROR ON ANALYSING DATA FOR RESOLUTION: {res}, SHIFT: {shift}, OFFSET: {offset}')
                        continue

    else:
        raise ValueError(f"INVALID MODE: {GENERAL_PARAMETERS['MODE']}. PLEASE TRY 'TEST', 'TRAIN', or 'V1'.")