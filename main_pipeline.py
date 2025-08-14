from datetime import date, datetime, timedelta
from db_ai_analysis_insert_pipeline import pipeline_insert_ai_analysis_in_db
from db_ai_canonical_insert_pipeline import pipeline_insert_ai_canonical_in_db
from db_caption_insert_pipeline import pipeline_insert_captions_in_db
from util.new_discounts_printer import print_unique_discount_records_since_datetime


def timed_step(description: str, func, *args, **kwargs):
    """
    Runs a pipeline step, prints start/finish messages, and returns the result.
    """
    print(f"**START {description}**")
    start = datetime.now()
    result = func(*args, **kwargs)
    end = datetime.now()
    print(f"**FINISHED {description} ({end - start})**\n")
    return result


def run_main_pipeline(inserted_at: date, post_date_after: datetime, cutoff_date: datetime):
    pipeline_start = datetime.now()
    print("**STARTING MAIN PIPELINE**")
    print(f"Start time: {pipeline_start.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # --- Captions ---
    timed_step("Instagram captions", pipeline_insert_captions_in_db, "instagram")
    timed_step("Instagram mention captions", pipeline_insert_captions_in_db, "instagram_mention")
    timed_step("TikTok captions", pipeline_insert_captions_in_db, "tiktok")

    # --- AI analysis ---
    timed_step("Instagram AI analysis", pipeline_insert_ai_analysis_in_db, "instagram", inserted_at, post_date_after)
    timed_step("TikTok AI analysis", pipeline_insert_ai_analysis_in_db, "tiktok", inserted_at, post_date_after)

    # --- AI canonical analysis ---
    timed_step("Instagram AI canonical analysis", pipeline_insert_ai_canonical_in_db, "instagram", cutoff_date)
    timed_step("TikTok AI canonical analysis", pipeline_insert_ai_canonical_in_db, "tiktok", cutoff_date)

    # --- Print results ---
    print("**PRINTING RESULTS**")
    print("**instagram results:**")
    print_unique_discount_records_since_datetime("instagram", cutoff_date, True)
    print("\n" * 5)
    print("**tiktok results:**")
    print_unique_discount_records_since_datetime("tiktok", cutoff_date, True)
    print("\n" * 5)

    pipeline_end = datetime.now()
    print("\n**FINISHED MAIN PIPELINE**")
    print(f"End time:   {pipeline_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {pipeline_end - pipeline_start}")


if __name__ == "__main__":
    #are input .txt files OK?
    #all api keys present?

    inserted_at = date(2025, 8, 13)
    post_date_after = datetime.now() - timedelta(days=3)
    cutoff_date = datetime(2025, 8, 13)
    run_main_pipeline(inserted_at, post_date_after, cutoff_date)
