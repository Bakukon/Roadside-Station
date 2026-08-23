from __future__ import annotations

from tsp.clients.ors_client import OrsClient
from tsp.clients.route_cache import RouteCache
from tsp.geojson_writer import write_geojson
from tsp.solvers.nearest_neighbor import solve as NN_solve
from tsp.models.tsp_context import TspContext
# from tsp.solvers.held_karp import solve as held_karp_solve
from tsp.tasks import resource_reader, tasks
from tsp.values import Const, Env


def main() -> None:
    visited = resource_reader.extract_visited_stations(
        tasks.read_trimmed_roadside_station(),
        tasks.read_visit_plan(),
        Const.TARGET_PREFECTURES,
    )
    diff_stations = resource_reader.extract_stations(tasks.read_roadside_station_diff())
    departure = resource_reader.extract_stations(tasks.read_departure_point())[0]

    michinoekis = [departure, *visited, *diff_stations]
    ors_client = OrsClient(Env.ORS_API_KEY, Const.ORS_PROFILE)
    route_cache = RouteCache(Const.ROUTE_CACHE_PATH, michinoekis)
    context = TspContext(michinoekis, departure, ors_client, route_cache)

    # initial_answer = NN_solve(context)
    answer = NN_solve(context)
    write_geojson(answer, Const.OUTPUT_PATH)


if __name__ == "__main__":
    main()
