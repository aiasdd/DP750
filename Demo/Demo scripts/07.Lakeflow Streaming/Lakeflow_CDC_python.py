# === PIPELINE SOURCE CODE (Python) ===
# Attach this notebook to a Lakeflow Pipeline — do not run cells directly

from pyspark import pipelines as dp
from pyspark.sql.functions import col

# — Bronze: Auto Loader — new maintenance CSV files from the landing volume ————
@dp.table
def maintenance_bronze():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format",         "csv")
            .option("cloudFiles.inferColumnTypes","true")
            .option("header",                    "true")
            .load("/Volumes/trainer_demo/demo_07/sensor_data_landing/maintenance_batch_*.csv")
    )

# — Silver: CDC — apply turbine status changes as SCD Type 2 ————————————
@dp.view
def turbine_cdc_feed_v2():
    return spark.readStream.table("trainer_demo.demo_07.turbine_events")

dp.create_streaming_table("turbines_silver")

dp.create_auto_cdc_flow(
    target          = "turbines_silver",
    source          = "turbine_cdc_feed",
    keys            = ["turbine_id"],
    sequence_by     = col("sequence_num"),
    apply_as_deletes = col("operation") == 'DELETE',
    except_column_list = ["operation", "sequence_num"],
    stored_as_scd_type = 2
)