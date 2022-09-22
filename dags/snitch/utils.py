def get_impact_of_escalation(escalation_rank, percent):
    return next(
        el['impact_value'] for el in escalation_rank if float(el['upper_bound']) > percent > float(el['lower_bound']))


def check_for_favorite(coef_t1, coef_t2):
    fav_team = None
    if abs(coef_t1 - coef_t2) >= 1.5:
        fav_team = 'Home' if coef_t1 < coef_t2 else 'Away'
    return fav_team


# def check_for_favorite(page_data):
#     fav_team = None
#     coef_t1, coef_t2 = get_coefs(page_data)
#     if abs(coef_t1 - coef_t2) >= 1.5:
#         fav_team = 'Home' if coef_t1 < coef_t2 else 'Away'
#     return fav_team


def get_coefs(page_data):
    coefs = page_data.query_selector_all('//span[@class="oddsValueInner"]')
    coef_t1 = float(coefs[0].inner_text())
    coef_t2 = float(coefs[2].inner_text())
    return [coef_t1, coef_t2]


def sort_matches():
    with open('/home/asus/PycharmProjects/snitch/data.yml', 'r') as file_to_read:
        yaml.dump(match_dict, outfile, default_flow_style=False)