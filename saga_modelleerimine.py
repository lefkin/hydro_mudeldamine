##!/usr/bin/python

import os, sys, subprocess, time

# SAGA PROGRAMMIFAILI ASUKOHT
saga_cmd = "C:\\Program Files\\QGIS 3.26.2\\apps\\saga\\saga_cmd"

# MÄÄRA TÖÖKATALOOG
os.chdir("C:\\Users\\priit.voolaid\\OneDrive - RMK\\Töölaud\\TMP\\LIDAR")

# MÄÄRA LIDAR-KÕRGUSMUDELI ASUKOHT
dem_tif = 'C:\\Users\\priit.voolaid\\OneDrive - RMK\\Töölaud\\TMP\\LIDAR\\dem.tif'

project = os.path.basename(dem_tif).split('.')[0]

# PAISUDE JOONTE KIHT
dam = 'C:\\Users\\priit.voolaid\\OneDrive - RMK\\Dokumendid\\PROJEKTID\\Laiküla\\paisud_10m_ristumisel.shp'

# KRAAVIDE KIHT
ditches = 'C:\\Users\\priit.voolaid\\OneDrive - RMK\\Töölaud\\TMP\\LIDAR\\kraavid.shp'

def runCommand(cmd, logerr):
	p = subprocess.run(cmd, stderr=logerr)

ERRLOG = "import.error.log" 
logerr = open(ERRLOG, 'w')

t0 = time.time()

#Filenames and variables for saga command inputs and outputs
dem_raw = 'dem_raw.sgrd'
dem_mosaick = '_dem_mosaick.sgrd'
dem_nosink = '_dem_nosink.sgrd'
flow_acc = '_flow_acc.sgrd'
ch_ntwk = '_ch_ntwk.sgrd'
ch_shapes = '_ch_shapes'
basins = '_basins'
subbasins = '_subbasins'
basins_vect = '_basins_vect'
subbasins_vect = '_subbasins_vect'
mouths = '_mouths'
dam_buffer = '_dams_with_buffer.shp'
dam_height = '_dams_with_height.shp'
column_name = 'dam_height'
dam_rast = '_dam_raster.sgrd'
ditches_rast = '_ditches_rast.sgrd'

# Import DEM tif-file
cmd_import =	([saga_cmd, 'io_gdal', '0',
				'-GRIDS', dem_raw,
				'-FILES', dem_tif,
				'-RESAMPLING 3'
], 'Import lidar DEM...')


# Preprocessing DEM
cmd_fillSinks = ([saga_cmd, 'ta_preprocessor', '3', 
				'-DEM', dem_raw, 
				'-RESULT', dem_nosink
], 'Fill sinks...')

# Create raster grid of ditches
cmd_ditches_rast = ([saga_cmd, 'grid_gridding', '0',
					'-INPUT', ditches,
					'-GRID', ditches_rast,
					'-OUTPUT 0', '-LINE_TYPE 1',
					'-TARGET_DEFINITION 1', '-TARGET_TEMPLATE', dem_raw,
], 'Create ditches raster layer...')

# Burn streams into DEM
cmd_burn_streams = ([saga_cmd, 'ta_preprocessor', '6',
					'-DEM', dem_raw,
					'-STREAM', ditches_rast, 
					'-METHOD 0', '-EPSILON 1'
], 'Burn streams into DEM...')


# Calculate flow accumulation
cmd_flowAcc =	([saga_cmd, 'ta_hydrology', '2',
				'-ELEVATION', dem_nosink,
				'-FLOW', flow_acc,
				'-METHOD 1'
], 'Generating flow accumulation trajectories...')

# Create channels
cmd_channels = ([saga_cmd, 'ta_channels', '0',
				'-ELEVATION', dem_nosink,
				'-CHNLNTWRK', ch_ntwk,
				'-SHAPES', ch_shapes,
				'-INIT_GRID', flow_acc,
				'-INIT_METHOD 2',
				'-INIT_VALUE 20000'
], 'Creating channels...')

# Create watershed basins
cmd_basins = 	([saga_cmd, 'ta_channels', '2',
				'-DEM', dem_nosink,
				'-CHANNELS', ch_ntwk,
				'-BASINS', basins,
				'-SUBBASINS', subbasins,
				'-V_BASINS', basins_vect,
				'-V_SUBBASINS', subbasins_vect,
				'-MOUTHS', mouths
], 'Drawing watershed basins...')

# Mosaick DEM and dams
cmd_mosaick =	([saga_cmd, 'grid_tools', '3',
				'-GRIDS', '{};{}'.format(dem_raw, dam_rast),
				'-OVERLAP 3',
				'-TARGET_DEFINITION 1',
				'-TARGET_TEMPLATE', dem_raw,
				'-TARGET_OUT_GRID', dem_mosaick
], 'Mosaicking DEM and dam raster...')

# Create buffers around dams
cmd_shapes_buffer =	([saga_cmd, 'shapes_tools', '18',
 					'-SHAPES', dam,
 					'-BUFFER', dam_buffer,
 					'-DIST_FIELD_DEFAULT 1',
 					'-DISSOLVE 0'
], 'Creating dam buffers...')

# Calculate zonal statistics for buffers, for dam height
cmd_shapes_stat =	([saga_cmd, 'shapes_grid', '2',
 					'-GRIDS', dem_raw,
 					'-POLYGONS', dam_buffer,
 					'-METHOD 2',
 					'-RESULT', dam_height,
 					'-MIN 0',  '-RANGE 0', '-SUM 0',
 					'-MEAN 0', '-VAR 0', '-STDDEV 0'
], 'Finding maximum cell value in dam buffer...')

# Specify final dam height
cmd_shapes_calc =	([saga_cmd, 'table_calculus', '2',
 					'-FORMULA [dem_raw (MAX)] +1',
 					'-NAME', column_name,
 					'-TABLE', dam_height,
 					'-RESULT', dam_height,
 					'-FIELD dem_raw (MAX)'
], 'Defining dam height...')

# Create dam grid from buffer polygons
cmd_buffer_to_grid =	([saga_cmd, 'grid_gridding', '0',
						'-INPUT', dam_height,
						'-FIELD', column_name,
						'-OUTPUT 2', '-GRID_TYPE 9',
						'-TARGET_DEFINITION 1',
						'-TARGET_TEMPLATE', dem_raw,
						'-GRID', dam_rast
], 'Creating dam raster...')

# Commands:
# 1. cmd_import
# 2. cmd_fillSinks
# 3. cmd_ditches_rast
# 4. cmd_burn_streams
# 5. cmd_flowAcc
# 6. cmd_channels
# 7. cmd_basins
# 8. cmd_mosaick
# 9. cmd_shapes_buffer		create buffer polygon for dams
# 10. cmd_shapes_stat		find maximum cell value on DEM inside buffer polygon 
# 11. cmd_shapes_calc		define dam height by adding to maximum cell value for each buffer
# 12. cmd_buffer_to_grid	rasterize dam buffer vector layer

# Dam grid generation steps in correct order
#make_dams = [cmd_import, cmd_shapes_buffer, cmd_shapes_stat, cmd_shapes_calc, cmd_buffer_to_grid]

# If you need to burn streams into DEM
burn_streams = [cmd_ditches_rast, cmd_burn_streams]

### MODELLEERIMISE KÄSUD!###
# TEOSTA HÜDROLOOGILINE MODELLEERIMINE KRAAVIDE KÕRVETAMISETA (kui sul ei ole kraavid digitud)
cmds = [cmd_import, cmd_fillSinks, cmd_flowAcc, cmd_channels, cmd_basins]

# KÕRVETA KRAAVID KÕRGUSMUDELILE JA TEOSTA HÜDROLOOGILINE MODELLEERIMINE
#cmds = [cmd_import] + burn_streams + [cmd_fillSinks, cmd_flowAcc, cmd_channels, cmd_basins]

# KÕRVETA KRAAVID KÕGUSMUDELILE, TEKITA KÕRGUSMUDELILE PAISUD JA TEE MODELLEERIMINE
#cmds = make_dams + burn_streams + [cmd_mosaick, cmd_fillSinks, cmd_flowAcc, cmd_channels, cmd_basins]

# TEKITA KÕRGUSMUDELILE PAISUD JA MODELLEERI HÜDROLOOGIAT!
#cmds = make_dams + [cmd_mosaick, cmd_fillSinks, cmd_flowAcc, cmd_channels]

dir_with_timestamp = str(time.time_ns())
dir_name = project + '_' + dir_with_timestamp
os.mkdir(dir_name)
os.chdir(dir_name)

for c, fb in cmds:
	if os.path.isfile('_dem_mosaick.sgrd') and c == cmd_fillSinks[0]:
		c[4] = '_dem_mosaick.sgrd'
	try:
		print(fb)
		runCommand(c, logerr)

	except Exception as e:
		logerr.write('Exception thrown while running command: {}\n'.format(c))
		logerr.write('ERROR: {}'.format(e))
		print(e)
		break

print("\nProcessing finished in " + str(int(time.time() - t0)) + " seconds.")
logerr.close()