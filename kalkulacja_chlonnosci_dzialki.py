from tabulate import tabulate, SEPARATING_LINE
import csv

def what_prompt(field):
    global table_rows

    table_rows[field][2] = input(f"{table_rows[field][1]} [{table_rows[field][3]}]: ")
    return table_rows

def check_parametr(field):
    global table_rows
    global float_value
    # float_value = 0

    # if isinstance(table_rows[field][2], float):  # check if value is already a floa
    try:
        if "," in str(table_rows[field][2]):
            table_rows[field][2] = table_rows[field][2].replace(",", ".")

        if table_rows[field][2] == "":
            table_rows[field][2] = 0.0

        if field < 11:
            float_value = float(table_rows[field][2])
            if float_value < 0.0:
                raise ValueError


        if field == 5:
            if float_value <= 3.5:
                print(f"Podałaś/eś złą wartość. Wysokość budynku musi być większa od 3. Wpisz ją jeszcze raz")
                what_prompt(5)
                check_parametr(5)

        if field == 11:
            if table_rows[11][2] not in ["M", "m", "B", "b"]:
                print ("""
                Podałaś/eś złą wartość,
                jeśli teren jest przeznaczony na mieszkania wpisz "M",
                jeśli teren jest przeznaczony na usługi lub biura wpisz "B".""")
                what_prompt(11).upper()
                check_parametr(11)
            else:
                float_value = table_rows[11][2].upper()

        if table_rows[3][2] == 0:
            if table_rows[4][2] == 0:
                print(f"""
                        jeden z parametrów musi być większy od zera.
                        Popraw 'współczynnik zabudowy' lub 'współczynnik intensywności zabudowy'""")
                what_prompt(3)
                what_prompt(4)
                check_parametr(3)
                check_parametr(4)

        if field == 0:
            if float(table_rows[0][2]) != max(float(table_rows[0][2]), float(table_rows[1][2]), float(table_rows[2][2])):
                print(f"""
                'Powierchnia działki musi być większa lub równa
                'terenowi pod zabudowę' oraz większa od
                'terenu pod którym może być podziemie'""")
                what_prompt(0)
                check_parametr(0)
            elif float(table_rows[0][2]) == max(float(table_rows[0][2]), float(table_rows[1][2]), float(table_rows[2][2])):
                float_value = float(table_rows[0][2])

    except ValueError:

            print (f"Podałaś/eś złą wartość. Podana odowiedź musi być liczbą dodatnią. Wpisz ją jeszcze raz")
            what_prompt(field)
            check_parametr(field)

    return float_value

def ask_for_amendment():
    global amendment
    global table_rows

    print(f"""
        PODAŁEŚ TAKIE PARAMETRY:
    {tabulate(table_rows, headers=["numer", "Parametr", "Wartość", "Jednostka"])}
    """)

    amendment = input("""
        JEŚLI CHCESZ POPRAWIĆ JEDEN Z PARAMETRÓW, WPISZ JEGO NUMER PORZĄDKOWY.
        JEŚLI WSZYSTKO SIĘ ZGADZA PRZEJDŹ DALEJ
        """)
    try:
        what_prompt(int(amendment)-1)
        check_parametr(int(amendment)-1)
    except:
        pass

    for field in range(len(table_rows)):
        check_parametr(field)

    ask_for_amendment
    return table_rows


def building_area():   # Building_area = wyliczenie powierzchni zabudowy
    global BA
    list = []

    if building_factor != 0:
        BAB = base * building_factor / 100
        list.append(BAB)
    elif building_factor == 0:
        BAB = 0
    if intensity_factor != 0:
        BAI = intensity_factor * base // count_floors()
        list.append(BAI)
    elif intensity_factor == 0:
        BAI = 0
        # BA = powierzchnia zabudowy
    BA = min(list)


    return BA


def total_area():   # total_area = wyliczenie powierzchni całkowitej
    global TA
    list = []

    if building_factor != 0:
        TAB = float(building_area() * (building_height // h))
        list.append(TAB)
# TAB = powierzchnia całkowita wyliczona na podstawie współczynnika zabudowy
    if intensity_factor != 0:
        TAI = base * intensity_factor
        list.append(TAI)
# TAI = powierzchnia całkowita wyliczona na podstawie intensywności  zabudowy
    TA = min(list)
    return TA

def count_floors():
    global floors_amount

    if building_height != 0:
        floors_amount = int(building_height // h)
    if building_height == 0:
        floors_amount = int((intensity_factor * base) // h)
    return floors_amount


def calculate_PUM():
    global PUM

    PUM = round((total_area() * 0.69), 2)
    return float(PUM)

def calculate_GLA():
    global GLA
    GLA = round((total_area() * 0.89), 2)
    return float(GLA)

def check_capability_for_underground_parking():
    global base_underground

    if base - base_underground < green_area_100:
        base_underground = base - green_area_100

    return base_underground,

# przyjmujemy że 4% wszystkich parkingów zajmują parkingi naziemne.
    # 1 miejsce parkingowe pod ziemią potrzebuje 35m2
    # 1 miejsce parkingowe na ziemi liczymy jako 12m,
    # bo przestrzeń manewrowa wliczona jest już w pomniejszenie współczynnika
    # biologicznie czynnego i zazwyczaj wykorzystuje drogę dojazdową do garażu lub ppoż.

def calculate_area_parkings_on_the_ground():
    global area_parkings_on_the_ground

    area_parkings_on_the_ground = 0.014257 * (base_underground * number_of_underground_floors)
    return area_parkings_on_the_ground

# Sprawdzenie czy zmieścimy na działce powierzchnie biologicznie czynną:
#   1. Najpierw zakładamy że 85% powierzchni dachów przeznaczmy na pow.
#   biol czynną(liczoną jako 50%)
#   2. potem dodajemy teren, który nie jest nad garażem i zakładamy że
#   w 80% przeznaczamy go na zieleń
#   3. potem dodajemy teren nad garażem który w 85% przeznaczony jest
#   na zieleń (liczoną jako 50%)
#   4. potem odejmujemy teren parkingów na powierzchni działki.
#   received_green =  building_area() * 0.85 * 0.5 + (base - base_underground) * 0.8 + (base_underground - building_area()) * 0,85 * 0,5 - area_parkings_on_the_ground =
#   = 0,425 * building_area() + 0,8 * base - 0,8 * base_underground + 0,425 * base_underground - 0,425 * building_area() - area_parkings_on_the_ground =
#   = 0,8 * base - 0,375 * base_underground - area_parkings_on_the_ground

def check_bioactiv_area():
    global received_green

    received_green = 0.8 * base - 0.375 * base_underground - area_parkings_on_the_ground

    if green_area - received_green > 0:
        print("""
        wymagana powierzchnia biologicznie czynna nie zmieści się na działce,
        nastąpi zmniejszenie parkingu podziemnego""")

    return received_green


    # jeżeli brakuje pow. biol czynnej musimy ją zwiększyć poprzez:
    # zmniejszenie parkingu podziemnego (underground/2) tak aby po za jego granicami była powierzchnia biol. czynna w 100% a nie 50%
    # musimy uzyskać conajmniej równość green_area = received_area.
    # zmniejszając ilość miejsc postojowych o 1 zmniejszamy powierzchnię zabudowy dwupoziomowego parkingu o 17.5m2


def revision():
    global base_underground
    global received_green
    global number_of_parkings
    global number_of_parkings_on_the_ground
    global number_of_parkings_underground

    X = int(base_underground // 17.5)

    for i in range(X):

        try:

        # base_underground = base_underground - 17.5
        # received_green = 0.8 * base - 0.375 * base_underground - area_parkings_on_the_ground
        # received_green =  0.8 * base - 0.375 * (base_underground - (35 / number_of_underground_floors)- area_parkings_on_the_ground) + (goal_flats_size / 1.2 / floors_amount)
        # received_green =  0.8 * base - (0.375 * base_underground) + (0.375 * (35 / number_of_underground_floors)) - area_parkings_on_the_ground + (goal_flats_size / 1.2 / floors_amount)

            if 'M' in destiny:
                received_green = received_green + (13.125 / number_of_underground_floors) + (PUM/((base_underground / 35 / number_of_underground_floors)+(area_parkings_on_the_ground/12))/ floors_amount)
            if 'B' in destiny:
                received_green = received_green + 6.56 + 1000/ 30 / floors_amount

            if received_green >= green_area:
                base_underground = base_underground - (i * (35 / number_of_underground_floors))
                number_of_parkings_underground = int(base_underground * number_of_underground_floors // 35)
                number_of_parkings_on_the_ground = int(area_parkings_on_the_ground // 12)
                number_of_parkings = int(number_of_parkings_on_the_ground + number_of_parkings_underground)
                break

        except ZeroDivisionError:

            received_green = received_green + 12
            base_underground = 0

            if received_green >= green_area:
                number_of_parkings = int((area_parkings_on_the_ground // 12) - i)
                number_of_parkings_underground = 0
                number_of_parkings_on_the_ground = int((area_parkings_on_the_ground // 12) - i)


    return base_underground, number_of_parkings, number_of_parkings_underground, number_of_parkings_on_the_ground


def calculate_average_size_of_app(parking_place_M):
    global average_size_of_app
    global parking_place_M_new

    try:
        average_size_of_app = round((PUM / (number_of_parkings / parking_place_M )),2)
        parking_place_M_new = parking_place_M
    except:
        print("""
            Nie Podałaś/eś ilości parkingów wymaganych przez MPZT.
            Jeśli nie są wymagane przez prawo, wpisz liczbę której oczekujesz.
            Musi być to liczba dodatnia""")
        what_prompt(8)
        parking_place_M_new = int(check_parametr(8))
        calculate_average_size_of_app(parking_place_M_new)

    return average_size_of_app, parking_place_M_new

def calculate_usable_area(parking_place_B):
    global usable_area
    global parking_place_B_new


    try:
        usable_area = float(number_of_parkings * 1000 / parking_place_B)
        usable_area = min(usable_area, GLA)
        parking_place_B_new = parking_place_B

    except ZeroDivisionError:
        print("""
            Nie Podałaś/eś ilości parkingów wymaganych przez MPZT.
            Jeśli nie są wymagane przez prawo, wpisz liczbę której oczekujesz.
            Musi być to liczba dodatnia""")
        what_prompt(9)
        parking_place_B_new = int(check_parametr(9))
        calculate_usable_area(parking_place_B_new)

    return usable_area, parking_place_B_new


if __name__ == "__main__":

    with open('assets\\base_variabile.csv', 'r', encoding='ANSI', errors='ignore') as fields:
        csvreader = csv.DictReader(fields)

    # Tworzymy słownik, w którym kluczami są nazwy pól, a wartościami są wprowadzone przez użytkownika wartości.
        data = {}

        for field in csvreader:
            prompt = f"{field['label']} [{field['unit']}]: "
            value = str(input(prompt))
            data[field['name']] = value

    # Tworzymy listę, która będzie składać się z wierszy tabeli
        table_rows = []
        csvreader = csv.DictReader(open('assets\\base_variabile.csv', 'r', encoding='ANSI', errors='ignore'))
        number = 0
        for field in csvreader:
            number = number + 1
            label = field['label']
            value = data[field['name']]
            unit = field['unit']
            table_rows.append([number, label, value, unit])

        print(tabulate(table_rows, headers=["#", "Label", "Value", "Unit"]))


    site_size = check_parametr(0)
    base = check_parametr(1)
    base_underground = check_parametr(2)
    building_factor = check_parametr(3)
    intensity_factor = check_parametr(4)
    building_height = check_parametr(5)
    green_area_percentage = check_parametr(6)
    green_area = green_area_percentage * base / 100
    green_area_100_percentage = check_parametr(7)
    green_area_100 = green_area_100_percentage * base / 100
    parking_place_M = check_parametr(8)
    parking_place_B = check_parametr(9)
    number_of_underground_floors = check_parametr(10)
    destiny = check_parametr(11)

    ask_for_amendment()

    if 'M' in destiny:
        h = 3
    if 'B' in destiny:
        h = 3.5

    building_area()
    total_area()
    count_floors()

    if building_factor == 0:
        BA = total_area() // floors_amount

    if 'M' in destiny:
        calculate_PUM()

    if 'B' in destiny:
        calculate_GLA()

    check_capability_for_underground_parking()
    calculate_area_parkings_on_the_ground()
    check_bioactiv_area()
    revision()

    if 'M' in destiny:
        parking_place_B = calculate_average_size_of_app(parking_place_B)[1]

    if 'B' in destiny:
        parking_place_M = calculate_usable_area(parking_place_M)[1]

    if 'M' in destiny:
        table = [
        ['powierzchnia działki', ' ', f'{site_size}m2', ' '],
        ['współczynnik zabudowy -> powierzchnia zabudowy', f'{building_factor}%',  f'{BA}m2', f'{round((BA/site_size*100), 2)}%'],
        ['intensywność zabudowy -> powierzchnia całkowita', f'{intensity_factor}', f'{TA}m2', f'{round((TA/site_size), 2)}'],
        ['powierzchnia biologicznie czynna', f'{green_area * 100 / base}%', f'{round(received_green, 2)}m2', f'{round((received_green / base * 100), 2)}%'],
        ['wymagana zieleń na gruncie', f'{green_area_100 * 100 / base}%', f'{green_area_100}m2', f'{round((green_area_100 / base * 100), 2)}%'],
        ['wysokość zabudowy', f'{building_height}m', f'{int(floors_amount)} kondygnacji', f'{building_height}m'],
        ['ilość mieszkań', ' ', int(PUM / average_size_of_app), ' '], SEPARATING_LINE,
        ['średnia wielkość mieszkania', ' ', f"{average_size_of_app}m2 lub większe", ' '],
        ['ilość miejsc postojowych razem', f'{parking_place_M_new} na mieszkanie', round(revision()[1], 2), f'{parking_place_M_new} na mieszkanie'],
        ['w tym ilość miejsc postojowych na poziomie terenu', '', number_of_parkings_on_the_ground, ''],
        ['w tym ilość miejsc postojowych w parkingu podziemnym', '', number_of_parkings_underground, ''], SEPARATING_LINE,
        ['ilość kondygnacji podziemnych', '', number_of_underground_floors, ''],
        ['współczynnik do liczenia PUM', ' ', 0.69, ' '], SEPARATING_LINE,
        ['PUM', '', f'{PUM}m2', '']]


    elif 'B' in destiny:
        table = [
        ['powierzchnia działki', ' ', f'{site_size}m2', ' '],
        ['współczynnik zabudowy -> powierzchnia zabudowy', f'{building_factor} %',  f'{BA}m2', f'{round((BA/site_size*100), 2)}%'],
        ['intensywność zabudowy -> powierzchnia całkowita', intensity_factor, f'{TA}m2', round((TA/site_size), 2)],
        ['powierzchnia biologicznie czynna', f'{green_area * 100 / base}%', f'{round(received_green, 2)}m2', f'{round((received_green / base * 100), 2)}%'],
        ['wymagana zieleń na gruncie', f'{green_area_100 * 100 / base}%', f'{green_area_100}m2', f'{round((green_area_100 / base * 100), 2)}%'],
        ['wysokość zabudowy', f'{building_height}m', f'{floors_amount} kondygnacji', f'{building_height}m'], SEPARATING_LINE,
        ['ilość miejsc postojowych razem', f'{parking_place_B_new} na 1000m2', round(revision()[1], 2), f'{round((number_of_parkings * 1000 / usable_area), 2)} na 1000m2'],
        ['w tym ilość miejsc postojowych na poziomie terenu', '', number_of_parkings_on_the_ground, ''],
        ['w tym ilość miejsc postojowych w parkingu podziemnym', '', number_of_parkings_underground, ''], SEPARATING_LINE,
        ['ilość kondygnacji podziemnych', '', number_of_underground_floors, ''],
        ['powierzchnia użytkowa obsłużona przez parkingi', '', f'{round(usable_area, 2)}m2', ' '],
        ['współczynnik do liczenia GLA', ' ', 0.89, ' '], SEPARATING_LINE,
        ['GLA', '', f'{GLA}m2', '']]

    print(tabulate((table), stralign = "center", headers = ['nazwa parametru', 'wymóg MPZT', 'osiągięte parametry', 'osiągnięte wskaźniki'], tablefmt="simple"),"\n")