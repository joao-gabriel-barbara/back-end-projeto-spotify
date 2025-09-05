from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from jobs import run_for_all_users, collect_top_artists, collect_top_tracks, collect_recently_played

# Cria o scheduler assíncrono
scheduler = AsyncIOScheduler()

def start_scheduler():
    """
    Adiciona os jobs assíncronos ao scheduler.
    Cada job roda a coroutine diretamente.
    """
    
    # Job de top artists a cada 5 minutos
    scheduler.add_job(
        func=run_for_all_users,
        trigger=IntervalTrigger(minutes=5),
        kwargs={"collect_function": collect_top_artists},
        max_instances=1
    )

    # Job de top tracks a cada 5 minutos
    scheduler.add_job(
        func=run_for_all_users,
        trigger=IntervalTrigger(minutes=5),
        kwargs={"collect_function": collect_top_tracks},
        max_instances=1
    )

    # Job de recently played a cada 5 minutos
    scheduler.add_job(
        func=run_for_all_users,
        trigger=IntervalTrigger(minutes=5),
        kwargs={"collect_function": collect_recently_played},
        max_instances=1
    )

    scheduler.start()
