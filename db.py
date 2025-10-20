attendings = []
#    {
#        'date' : None,
#        'ФИО' : str,
#        'пара' : str
#    }

current_pairs = []
 
def get_pairs():
    return current_pairs

def add_attender(name, date, pair):
    """Добавление посещения"""
    attendings.append(
        {
            'date' : date,
            'name' : name,
            'pair_name' : pair
        }
)

def admin_add_pairs(the_day):
    current_pairs.extend(the_day)
    print(current_pairs)