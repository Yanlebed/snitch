import logging
import operator
from collections import OrderedDict, Counter
from math import ceil

# for remote run
from snitch.utils import get_impact_of_escalation, check_for_favorite

# for local run
# from dags.snitch.utils import get_impact_of_escalation, check_for_favorite

FAV = None

FIRST_HALF_LINK = "https://www.flashscore.com/match/{match_id}/#/match-summary/match-statistics/1"
SECOND_HALF_LINK = "https://www.flashscore.com/match/{match_id}/#/match-summary/match-statistics/2"
# FIRST_HALF_LINK = "https://www.flashscore.com/match/GCpocjRk/#/match-summary/match-statistics/1"
# SECOND_HALF_LINK = "https://www.flashscore.com/match/GCpocjRk/#/match-summary/match-statistics/2"

STATS = {
    'Minute': None,
    'Home': {
        'Fav': False,
        'Shots on Goal': None,
        'Shots off Goal': None,
        'Corner Kicks': None,
        'Red Cards': None,
        'Dangerous Attacks': None,
    },
    'Away': {
        'Fav': False,
        'Shots on Goal': None,
        'Shots off Goal': None,
        'Corner Kicks': None,
        'Red Cards': None,
        'Dangerous Attacks': None,
    },
}

ESCALATION_RANK = [
    {'lower_bound': 0, 'upper_bound': 12, 'impact_value': -0.25},
    {'lower_bound': 13, 'upper_bound': 33, 'impact_value': 0},
    {'lower_bound': 34, 'upper_bound': 69, 'impact_value': 0.25},
    {'lower_bound': 70, 'upper_bound': 999999999, 'impact_value': 0.5},
]


class DetailsCollector(object):

    def __init__(self, match_id):
        self.match_id = match_id
        self.fav = None

    def parse(self):
        pass
        # with sync_playwright() as p:
        #     browser = p.chromium.launch(headless=False, slow_mo=500)
        #     page = browser.new_page()
        #
        #     # page.goto(first_half_link) # 'https://www.flashscore.com/match/vFsBsev0/#/match-summary'
        #     page.goto('https://www.flashscore.com/match/vFsBsev0/#/match-summary')
        #
        #     self.fav = check_for_favorite(page)
        #
        #     if not self.fav:
        #         logging.info('No favourite in this match')
        #         return None

    #         stats[fav]['Fav'] = True
    #
    # stats_categories = page.query_selector_all('//div[@class="stat__category"]')
    # # minutes = page.query_selector_all('//div[@class="detailScore__status"]/span')[1].inner_text().replace('-', '').strip()
    # # stats['Minute'] = minutes
    # for category in stats_categories:
    #     category_name = category.query_selector('//div[@class="stat__categoryName"]').inner_text()
    #     if 'Shots on Goal' in category_name:
    #         stats['Home']['Shots on Goal'] = category.query_selector('//div[@class="stat__homeValue"]').inner_text()
    #         stats['Away']['Shots on Goal'] = category.query_selector('//div[@class="stat__awayValue"]').inner_text()
    #     elif 'Shots off Goal' in category_name:
    #         stats['Home']['Shots off Goal'] = category.query_selector('//div[@class="stat__homeValue"]').inner_text()
    #         stats['Away']['Shots off Goal'] = category.query_selector('//div[@class="stat__awayValue"]').inner_text()
    #     elif 'Corner Kicks' in category_name:
    #         stats['Home']['Corner Kicks'] = category.query_selector('//div[@class="stat__homeValue"]').inner_text()
    #         stats['Away']['Corner Kicks'] = category.query_selector('//div[@class="stat__awayValue"]').inner_text()
    #     elif 'Corner Kicks' in category_name:
    #         stats['Home']['Corner Kicks'] = category.query_selector('//div[@class="stat__homeValue"]').inner_text()
    #         stats['Away']['Corner Kicks'] = category.query_selector('//div[@class="stat__awayValue"]').inner_text()
    #     elif 'Red Cards' in category_name:
    #         stats['Home']['Red Cards'] = category.query_selector('//div[@class="stat__homeValue"]').inner_text()
    #         stats['Away']['Red Cards'] = category.query_selector('//div[@class="stat__awayValue"]').inner_text()
    #     elif 'Dangerous Attacks' in category_name:
    #         stats['Home']['Dangerous Attacks'] = category.query_selector('//div[@class="stat__homeValue"]').inner_text()
    #         stats['Away']['Dangerous Attacks'] = category.query_selector('//div[@class="stat__awayValue"]').inner_text()
    #
    # print(page.title())
    # browser.close()
    # # page.query_selector('//div[@class="smv__participantRow smv__awayParticipant"]//*[contains(text(), "Yellow card / Red card")]')
    # # page.query_selector('//div[@class="smv__participantRow smv__awayParticipant"]//*[contains(@class, "card-ico yellowCard-ico")]')
    # # page.query_selector('//div[@class="smv__participantRow smv__awayParticipant"]//*[contains(@class, "card-ico redCard-ico")]')
    #
    # # value of stats
    # on_goal_value = 2
    # off_goal_value = 1
    # corner_value = 1
    # dang_attacks_value = 0.5
    #
    # # 15 minutes stats
    # fav_on_goal_15_min = 1
    # fav_off_goal_15_min = 2
    # fav_corners_15_min = 1
    # fav_dang_attacks_15_min = 15
    # # if dang_attacks < 10 we don't take into account this 15 minutes segment
    #
    # outsider_on_goal_15_min = 1
    # outsider_off_goal_15_min = 0
    # outsider_corners_15_min = 1
    # outsider_dang_attacks_15_min = 11
    # # if dang_attacks < 10 we don't take into account this 15 minutes segment
    #
    # fav_percent_of_escalation_15_min = (fav_on_goal_15_min * on_goal_value) + (fav_off_goal_15_min * off_goal_value) + (
    #         fav_corners_15_min * corner_value) * 100 / fav_dang_attacks_15_min
    # outsider_percent_of_escalation_15_min = (outsider_on_goal_15_min * on_goal_value) + (
    #         outsider_off_goal_15_min * off_goal_value) + (
    #                                                 outsider_corners_15_min * corner_value) + (
    #                                                 outsider_dang_attacks_15_min * dang_attacks_value)
    #
    # fav_impact_of_escalation_15_min = get_impact_of_escalation(ESCALATION_RANK, fav_percent_of_escalation_15_min)
    # outsider_impact_of_escalation_15_min = get_impact_of_escalation(ESCALATION_RANK, outsider_percent_of_escalation_15_min)
    #
    # # H2H, 5 last matches
    # fav_scores_goals = [1, 1, 2, 2, 1]
    # # Забивают ли они 1 (если да, ожидается 1), забивают ли 2 (забивают в 2 матчах из 5, возможно ожидается 2).
    # # Значит они точно забьют 1 и скорее всего забьют 2 (приблизительно 1.75).
    #
    # out_concedes_goals = [0, 1, 2, 1, 1]
    # # в 4 матчах из 5 пропустил 1 гол (в 1 - 0 пропущенных, в 1 - 2 пропущенных).
    # # Значит это влияет на 1.75 в сторону уменьшения.
    #
    # fav_concedes_goals = [1, 1, 1, 2, 2]
    # # в 4 из 5 пропустил хотя бы 1 гол (в 2 случаях пропустил 2).
    #
    # out_scores_goals = [1, 1, 1, 1, 1]
    #
    # # во всех матчах забивает 1.
    #
    # # Определяется нижняя грань, которую точно забивает.
    # # Забивает ли 1? Забивает ли 2? (1 из 5 - 1.25; 2 из 5 - 1.5; 3 из 5, 4 из 5 - 1.75; 5 из 5 - 2 и это становится новой нижней гранью).
    # # Соперник: определяем нижнюю грань, которую точно пропускает. (логика такая же). Эвертон - 0.75 по пропущенным.
    #
    # dict_of_decimal_parts = {
    #     1: 0.25,
    #     2: 0.5,
    #     3: 0.75,
    #     4: 0.75,
    #     5: 1
    # }
    #
    # expected_fav = 1.75
    # expected_out = 1.25
    #
    # # РАСЧЕТ ОЖИДАНИЯ ПЕРВОГО ТАЙМА
    # # разница доматчевых эспектед фаворита и экспектед аутсайдера, деленная на 2.
    # # (если разница между экспетдами 1.75 (2.75, 3.75) - округляем до большего)
    # # если сумма экспектедов больше или равна 3 - увеличиваем ОЖИДАНИЕ ПЕРВОГО ТАЙМА на 0.25
    # # если ОЖИДАНИЕ 1Т 0.5 - не отслеживается до второго тайма.
    # difference_of_expected = abs(expected_fav - expected_out)
    # first_time_expectation = difference_of_expected / 2
    #
    # if difference_of_expected % 1 == 0.75:
    #     first_time_expectation = ceil(first_time_expectation)
    # elif expected_fav + expected_out >= 3:
    #     first_time_expectation += 0.25
    #
    # if first_time_expectation <= 0.5:
    #     print('First time of this match is not interesting for us.')
    #     # add flag for first time, check_first_time = False
    #
    # # В ХАЛФТАЙМЕ
    # # плюсуем доматчевые экспектеды и делим пополам = экспектед на второй тайм.
    # # если у команды статистика в перерыве 0.5 - плюсуем 0.25 к экспектеду на 2Т. если статистика 0.25 - то остается прежним.
    # # если 0 - минус 0.25, если -0.25 - то минус 0.5
    #
    # second_time_expectation = (expected_fav + expected_out) / 2
    # # half_time_stat_fav = ...
    # # half_time_stat_out = ...
    # half_time_stat_fav = 0.5
    # half_time_stat_out = 0.25
    #
    # if half_time_stat_fav >= 0.5:
    #     second_time_expectation += 0.25
    # elif half_time_stat_fav == 0:
    #     second_time_expectation -= 0.25
    # elif half_time_stat_fav == -0.25:
    #     second_time_expectation -= 0.5
    #
    # def process_goals_info(goals_list):
    #     score_to_return = 0
    #     majority_goals_value = 0
    #     majority_goals_qty = 0
    #     for ind, goals_and_qty in enumerate(goals_list):
    #         if ind == 0:
    #             majority_goals = goals_and_qty[0]
    #             score_to_return = goals_and_qty[0] + 1
    #             majority_goals_qty = goals_and_qty[1]
    #
    #     # for ind, goals_and_qty in enumerate(goals_list):
    #     #     if ind == 0:
    #     #         majority_goals = goals_and_qty[0]
    #     #         score_to_return = goals_and_qty[0] + 1
    #     #         majority_goals_qty = goals_and_qty[1]
    #     #     else:
    #     #         if goals_and_qty[0] > majority_goals_value:
    #     #             score_to_return += 0.25
    #     #         else:
    #     #             score_to_return -= 0.25
    #
    # def get_score(team_scores, team_concedes):
    #     team_scores_counter = Counter(team_scores)
    #     team_concedes_counter = Counter(team_concedes)
    #
    #     team_scores_counter_descending = sorted(team_scores_counter.items(), key=operator.itemgetter(1), reverse=True)
    #     team_concedes_counter_descending = sorted(team_concedes_counter.items(), key=operator.itemgetter(1),
    #                                               reverse=True)
    #
    #     teams_scores_digit = process_goals_info(team_scores_counter_descending)
    #
    #     return True
    #
    # fav_score = get_score(fav_scores_goals, fav_concedes_goals)
    # outsider_score = get_score(out_scores_goals, out_concedes_goals)
