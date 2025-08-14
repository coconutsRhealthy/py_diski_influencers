from datetime import date, datetime, timedelta
from db_ai_analysis_insert_pipeline import pipeline_insert_ai_analysis_in_db
from db_ai_canonical_insert_pipeline import pipeline_insert_ai_canonical_in_db
from db_caption_insert_pipeline import pipeline_insert_captions_in_db
from util.new_discounts_printer import print_unique_discount_records_since_datetime


def run_main_pipeline(inserted_at: date, post_date_after: datetime, cutoff_date: datetime):
    starttime = datetime.now()

    #caption inserts...
    print("**STARTING MAIN PIPELINE**")
    print("** starttime: " + starttime + " **")

    print()
    print("**START INSERTING CAPTIONS**")
    print("**start inserting instagram user captions**")
    pipeline_insert_captions_in_db("instagram")
    print("**finished inserting instagram user captions**")
    print()
    print("**start inserting instagram_mention captions**")
    pipeline_insert_captions_in_db("instagram_mention")
    print("**finished inserting instagram_mention captions**")
    print()
    print("**start inserting tiktok captions**")
    pipeline_insert_captions_in_db("tiktok")
    print("**finished inserting tiktok captions**")

    print("\n" * 5)

    #ai analysis...
    print("**START INSERTING AI ANALYSIS**")
    print("**start inserting instagram ai analysis**")
    pipeline_insert_ai_analysis_in_db("instagram", inserted_at, post_date_after)
    print("**finished inserting instagram ai analysis**")
    print("**start inserting tiktok ai analysis**")
    pipeline_insert_ai_analysis_in_db("tiktok", inserted_at, post_date_after)
    print("**finished inserting tiktok ai analysis**")

    print("\n" * 5)

    #ai canonical...
    print("**START INSERTING AI CANONICAL ANALYSIS**")
    print("**start inserting instagram ai canonical analysis**")
    pipeline_insert_ai_canonical_in_db("instagram", cutoff_date)
    print("**finished inserting instagram ai canonical analysis**")
    print("**start inserting tiktok ai canonical analysis**")
    pipeline_insert_ai_canonical_in_db("tiktok", cutoff_date)
    print("**finished inserting tiktok ai canonical analysis**")

    print("\n" * 8)

    #print results...
    print("**PRINTING RESULTS**")
    print("**instagram results:**")
    print_unique_discount_records_since_datetime("instagram", cutoff_date, True)

    print("\n" * 5)

    print("**tiktok results:**")
    print_unique_discount_records_since_datetime("tiktok", cutoff_date, True)

    print("\n" * 5)
    print("**FINISHED MAIN PIPELINE**")
    print()

    endtime = datetime.now()
    duration = endtime - starttime
    print(f"Start time: {starttime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time:   {endtime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration:   {duration}")



if __name__ == "__main__":
    inserted_at = date(2025, 8, 13)
    post_date_after = datetime.now() - timedelta(days=3)
    cutoff_date = datetime(2025, 8, 13)
    run_main_pipeline(inserted_at, post_date_after, cutoff_date)