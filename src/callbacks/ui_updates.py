import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback_context
from src.Logger import Logger
from src.utils.callback_utils import _generate_donut_chart_data
from cache_manager import get_all_users_data

logger = Logger(__name__).get_logger()


def update_repeat_penalty_badge(value):
    return f"{value:.2f}"


def update_temperature_badge(value):
    return f"{value:.2f}"


def update_top_k_badge(value):
    return str(int(value))


def update_top_p_badge(value):
    return f"{value:.2f}"


def toggle_scores_modal(n_clicks, opened):
    if n_clicks:
        return not opened, dash.no_update
    return opened, dash.no_update


def update_donut_chart(n_intervals, modal_opened, cache):
    """
    Met à jour le graphique en forme de donut avec les statistiques des utilisateurs.
    """
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    force_update = triggered_id == "scores-modal" and modal_opened

    if n_intervals is None and not force_update:
        return dash.no_update

    all_users_data = get_all_users_data(cache)
    data = _generate_donut_chart_data(all_users_data)

    return dmc.DonutChart(
        data=data,
        size=300,
        thickness=40,
        withTooltip=True,
        tooltipDataSource="segment",
        chartLabel=f"Total: {sum(item['value'] for item in data)}",
        style={"margin": "auto"},
    )
