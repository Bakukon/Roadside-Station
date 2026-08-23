from __future__ import annotations

from tsp_kanto.clients.distance_client import DistanceClient
from tsp_kanto.geojson_writer import write_geojson
from tsp_kanto.models.tsp_context import TspContext
from tsp_kanto.solvers.nearest_neighbor import solve as NN_solve
from tsp_kanto.solvers.two_opt_ILS_or_opt import solve as two_opt_ILS_or_ops
from tsp_kanto.tasks import resource_reader, tasks
from tsp_kanto.values import Const


def main() -> None:
    abolished_names = [
        p.name for p in resource_reader.extract_stations(tasks.read_roadside_station_abolished())
    ]
    excluded_names = [*tasks.read_excepted_from_kanto(), *abolished_names]

    all_target_stations = resource_reader.extract_target_stations(
        tasks.read_trimmed_roadside_station(),
        Const.TARGET_PREFECTURES,
        excluded_names,
    )
    departure = next(p for p in all_target_stations if p.name == Const.DEPARTURE_STATION_NAME)
    target_stations = [p for p in all_target_stations if p != departure]
    diff_stations = resource_reader.extract_stations(tasks.read_roadside_station_diff())

    michinoekis = [departure, *target_stations, *diff_stations]
    context = TspContext(michinoekis, departure, DistanceClient())

    initial_answer = NN_solve(context)
    answer = two_opt_ILS_or_ops(context, initial_answer)
    write_geojson(answer, Const.OUTPUT_PATH)


if __name__ == "__main__":
    main()
