import io
from datetime import date, datetime, timedelta
from multiprocessing.pool import ThreadPool
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import dateutil.parser

from imdb import Cinemagoer
import jellyfish



class Vox(object):

    whatson_soup = BeautifulSoup(requests.get("https://uae.voxcinemas.com/movies/whatson").content, "html.parser",
                                 from_encoding='utf-8')

    comingsoon_soup = BeautifulSoup(requests.get("https://uae.voxcinemas.com/movies/comingsoon").content, "html.parser",
                                   from_encoding='utf-8')


    whats_on_links_list = []
    whats_on_names_list = []
    coming_soon_links_list = []
    coming_soon_names_list = []
    def __init__(self):
        self.links = []
        self.info = []
        self.desc = []
        self.tmdb_apikey = "d0d0ea1e5157d5c8a1206d6cbf5877d0"
        self.tmdb_link = "https://api.themoviedb.org/3/search/movie?api_key=" + self.tmdb_apikey + "{}"


    @classmethod
    def whatson_links(cls):
        for shiuf in cls.whatson_soup.find_all("a", {"class": "action secondary"}):
            linkhref = re.sub("#showtimes", "", shiuf["href"])
            cls.whats_on_links_list.append("https://uae.voxcinemas.com" + linkhref)
        return cls.whats_on_links_list

    @classmethod
    def whatson_names(cls):
        for shiuf in cls.whatson_soup.select('h3'):
            cls.whats_on_names_list.append(shiuf.text)
        return cls.whats_on_names_list

    @classmethod
    def comingsoon_links(cls):
        for shiuf in cls.comingsoon_soup.find_all("article", {"class": "movie-summary"}):
            for shiuf1 in shiuf.find_all("a", {"class": "action primary outline"}):
                linkhref = re.sub("#showtimes", "", shiuf1["href"])
                cls.coming_soon_links_list.append("https://uae.voxcinemas.com" + linkhref)
        return cls.coming_soon_links_list

    @classmethod
    def comingsoon_names(cls):
        for shiuf in cls.comingsoon_soup.select('h3'):
            cls.coming_soon_names_list.append(str(shiuf).split("</span> ")[1].split("</a></h3>")[0])
        return cls.coming_soon_names_list

    def validate_whatson_injson(self):
        shui1 = []
        for i in self.whatson_soup.find_all("p", {"class": "language"}):
            shui1.append(re.sub("Language: ", "", i.text).lower().strip())

        shui = []
        for i in self.whatson_names():
            shui.append(re.sub('[^A-Za-z0-9]+', '', i.lower()))

        with open('ids.json', "r") as file:
            data = json.load(file)

        json_keys = [k for d in data["ids"] for k in d]  # keys in json file
        for i in [x + y for x, y in zip(shui, shui1)]:  # Name + language
            if not i in json_keys and not (max([jellyfish.jaro_winkler_similarity(i.lower(), c) for c in
                                                json_keys])) > 0.85:  # keys in json file
                last_num = (([z for d in data["ids"] for k, z in d.items()])[-1])
                data["ids"].append({i: last_num + 1})

        with open('ids.json', "w") as file:
            json.dump(data, file)

        print(shui1)

    @staticmethod
    def location_cinema(cinema: str):
        locations = {
            "dubai": [
                "Burjuman",
                "City Centre Deira",
                "City Centre Mirdif",
                "Mall of the Emirates",
                "MEGAPLEX(Cineplex Grand Hyatt)",
                "Nakheel Mall",
                "Wafi Mall at Wafi City",
                "Kempinski Hotel at MOE",
                "Mercato",
                "City Centre Shindagha",
                "OUTDOOR at Aloft Dubai Creek",
                "OUTDOOR at Galleria - Dubai"
            ],
            "sharjah": [
                "City Centre Al Zahia",
                "City Centre Sharjah",
            ],
            "Fujairah": [
                "City Centre Fujairah",
            ],
            "Abu Dhabi": [
                "Nation Towers - Abu Dhabi",
                "Yas Mall - Abu Dhabi",
                "Abu Dhabi Mall - Abu Dhabi",
                "The Galleria Al Maryah Island",
                "Marina Mall - Abu Dhabi"

            ],
            "Ras Al Khaimah": [
                "Al Hamra Mall - Ras Al Khaimah"

            ],
            "alain": [
                "Al Jimi Mall",

            ],
            "Ajman": [
                "City Centre Ajman",
            ]
        }
        loc_list = []
        for banshoza, kuuyyo in locations.items():
            loc_list.append(kuuyyo)
        scores = {}
        for iiias in [x for xs in loc_list for x in xs]:
            scores[iiias] = jellyfish.jaro_winkler_similarity(cinema, iiias)
        salazoiu = list(scores.keys())[list(scores.values()).index(max(scores.values()))] if max(
            scores.values()) > 0.55 else None
        for emirates, y in locations.items():
            a = (locations[emirates])
            try:
                _ = a.index(salazoiu)
                return list(locations.keys())[list(locations.values()).index(a)]
            except ValueError:
                pass

    @staticmethod
    def __numbers_to_words(number):  # https://stackoverflow.com/a/35794203
        number2word = {'1': "one", '2': "two", '3': "three", '4': "four", '5': "five", '6': "six",
                       '7': "seven", '8': "eight", '9': "nine", '0': "zero"}
        return " ".join(map(lambda ind: number2word[ind], str(number)))

    def sheeeeeeesh(self,
                    link: str,
                    day: str | int = "today",
                    types_to_show:    tuple | str  | list        = ("all", True),
                    cinemas_to_show:  tuple | str  | list        = ("all", True),
                    emirates_to_show: tuple | str  | list | None = ("all", True),
                    tmdb:bool = False,
                    imdb:bool = False):

        if day == "today":
            thetime = date.today().strftime("%Y%m%d")
        elif isinstance(day, int):
            date_1 = datetime.strptime(date.today().strftime("%Y%m%d"), "%Y%m%d")
            modified_date = date_1 + timedelta(days=day)
            thetime = datetime.strftime(modified_date, "%Y%m%d")
        else:
            raise Exception("Wrong time format, use 'today' for today time, else use an integer to add said days to "
                            "todays date")
        
        main_page = BeautifulSoup(requests.Session().get(link + "?d={}".format(thetime)).text, "html.parser")

        info = {}
        for i in io.StringIO(
                BeautifulSoup(
                    str(main_page.select('aside')), features="lxml").get_text().strip('[]\n').rstrip('\n')):
            info[i.strip("\n").split(': ')[0]] = \
                i.strip("\n").split(': ')[1]
        try:
            _ = info["Running Time"]
        except KeyError:
            info["Running Time"] = ""
        try:
            info["Starring"] = info["Starring"].split(",")
        except KeyError:
            pass

        title_main = BeautifulSoup(str(main_page.select('h1')), features="lxml").get_text().strip("[]")



        imdbinfo = {}
        if imdb:
            imdbinfo.clear()
            imdbinfo = {'name': None,'rating': None, 'votes': None}
            ia = Cinemagoer()
            break1 = 0
            for i in ia.search_movie(str(title_main)):
                if i['kind'] == 'movie':
                    break1 = 1
                    z = ia.get_movie(i.movieID)
                    try:
                        imdbinfo['rating'] = (z['rating'])
                        imdbinfo['votes']  = (z['votes'])
                        imdbinfo['name']   = str(i)
                    except KeyError:
                        pass
                if break1 == 1:
                    break

        tmdb_status = 0
        if title_main == "404 Error":
            # print(main_page)
            pass

        tmdb_info = {}
        try:
            if tmdb:

                tmdb_request_nojson = requests.get(self.tmdb_link.format("&query={}".format(title_main)))
                tmdb_request = tmdb_request_nojson.json()
                if tmdb_request_nojson.status_code != 200:
                    tmdb_status = 0

                if len(tmdb_request["results"]) == 0:
                    tmdb_status = 0
                try:
                    if [z[1] for z in json.load(open('iso639.json', "r")) if z[1].lower() in info["Language"].lower()] != \
                            [z[1] for z in json.load(open('iso639.json', "r")) if z[0].lower() in tmdb_request["results"][0]["original_language"].lower()]:
                        tmdb_status = 0
                        raise IndexError

                    if jellyfish.jaro_winkler_similarity(str(title_main), str(tmdb_request["results"][0]["title"])) < 0.9:
                        tmdb_status = 0
                    else: tmdb_status = 1

                    if tmdb_status == 0:
                        try:
                            match = re.search('\d', str(tmdb_request["results"][0]["title"]))
                            num = self.__numbers_to_words(match.group(0))
                            new_title = re.sub('\d', num, str(tmdb_request["results"][0]["title"]))
                            if jellyfish.jaro_winkler_similarity(str(new_title).lower(),
                                                                 str(title_main).lower()) < 0.9:
                                raise AttributeError
                            else: tmdb_status = 1


                        except AttributeError: pass
                        except KeyError:pass
                        except ValueError:pass



                    else:tmdb_status = 1
                except IndexError: pass
                except ValueError:pass
                print(tmdb_status)
                if tmdb_status == 1:
                    fop = requests.get("https://api.themoviedb.org/3/movie/" + str(
                        tmdb_request["results"][0]["id"]) + "/credits?api_key={}&language=en-US".format(
                        self.tmdb_apikey)).json()
                    actors = []
                    for i in (fop["cast"])[0:7]:
                        try:
                            actors.append({"name": i["name"],
                                           "pic": "https://image.tmdb.org/t/p/original" + i["profile_path"],
                                           "charecter_name": i["character"]})
                        except TypeError:
                            pass
                    tmdb_info.update({
                        "actors_info":actors,
                        "tmdb_genre": [k['name'] for k in json.load(open('tmdb_genres.json', "r"))['genres'] if k['id'] in
                           tmdb_request["results"][0]["genre_ids"]],
                        "tmdb_vote_average": tmdb_request["results"][0]["vote_average"],
                        "tmdb_vote_count": tmdb_request["results"][0]["vote_count"],
                        "tmdb_img": "https://image.tmdb.org/t/p/original" + tmdb_request["results"][0]["poster_path"]


            })
        except  KeyError:
            pass
        summary = lambda numbee: BeautifulSoup(str(main_page.select('article:nth-child({}) > p'.format(numbee))),
                                               features="lxml").get_text().strip("[]")
        main_content = {
            "title":
                title_main,
            # "id":tmdb_request["results"][0]["id"],
            "info": info,
            "tmdb_info":tmdb_info,
            "imdb": imdbinfo,
            "img": main_page.select(".lazy:nth-child(3)")[0]["data-src"],
            "yt-embed": main_page.find_all('iframe')[1]["src"] if len(main_page.find_all('iframe')) == 2 else "",
            "yt-link": "https://www.youtube.com/watch?v=" +
                       main_page.find_all('iframe')[1]["src"].split("?rel", 1)[0].split("embed/", 1)[1] if len(
                main_page.find_all('iframe')) == 2 else "",
            "rating": BeautifulSoup(str(main_page.select('.classification')), features="lxml").get_text().strip("[]"),
            "summary": summary(4) if summary(4) != "" else summary(3),
            "showings": {}
        }

        for outer_frame_shows in main_page.select('.region-ae .dates'):
            for index_showtimes, showtimes in enumerate(outer_frame_shows.find_all("ol", {"class": "showtimes"})):
                cinemas_title = outer_frame_shows.find_all(  # ╔════════════════════════════════╗
                    "h3", {"class": "highlight"})[index_showtimes].get_text()  # ║         CINEMA NAME[2]         ║
                main_content["showings"][cinemas_title] = {}  # ╚════════════════════════════════╝
                for outer_timings in showtimes.find_all('li'):  # ─────TIMINGS links and times text──────

                    main_content["showings"][cinemas_title]["all"] = {}
                    timings = {}
                    for inner_timings in outer_timings.find_all(
                            'li'):  # ═══════════════════════════TIMINGS[0]══════════════════════════╗
                        for _, available_timings in enumerate(
                                inner_timings.find_all("a", {"class": "action showtime"})):  # ║
                            timings.update({available_timings.get_text().strip(): "https://uae.voxcinemas.com" +
                                                                                  available_timings['href']})  # ║
                            # ║
                        for _, unavailable_timings in enumerate(
                                inner_timings.find_all("span", {"class": "action showtime unavailable"})):  # ║
                            timings.update({
                                               unavailable_timings.get_text(): None})  # ═════════════════════════════════════════════════╝

                    main_content["showings"][cinemas_title]["all"].update(timings)

                    try:  # ═══════════════════════════SHOWING TYPE[1]═══════════════════════╗
                        ozy = outer_timings.find('strong').get_text()  # ║
                        main_content["showings"][cinemas_title][ozy] = main_content["showings"][cinemas_title].pop(
                            "all")  # ║
                    except AttributeError:
                        pass  # ║
                try:  # ║
                    _ = main_content["showings"][cinemas_title]["all"]  # ║
                    main_content["showings"][cinemas_title].pop("all")  # ║
                except KeyError:  # ║
                    pass  # ══════════════════════════════════════════════════════════════════════════════════╝

        # ═════════════════MOVIE TYPE FILTER════════════════
        if isinstance(types_to_show, str):
            types_to_show = ([types_to_show], True)
        elif isinstance(types_to_show, list):
            types_to_show = (types_to_show, True)
        elif isinstance(types_to_show, tuple):
            if isinstance(types_to_show[0], str):
                types_to_show = ([types_to_show[0]], types_to_show[1])
            elif isinstance(types_to_show[0], list):
                types_to_show = (types_to_show[0], types_to_show[1])

        if str(types_to_show[0][0]).lower() != "all":
            types = []
            contin = 0
            warnme = 0
            prev_type = []
            for cinema_name, cinema_value in main_content["showings"].items():
                for showing_type, showing_content in cinema_value.items():
                    for user_types in types_to_show[0]:
                        if jellyfish.jaro_winkler_similarity(re.sub('[^A-Za-z0-9]+', '', showing_type.lower()),
                                                             re.sub('[^A-Za-z0-9]+', '', re.sub('[^A-Za-z0-9]+', '', str(user_types).lower()))) > 0.9285:
                            types.append({cinema_name: {showing_type: showing_content}})

                            if not user_types in prev_type:
                                prev_type.append(user_types)
                                warnme += 1


            if types_to_show[1]:
                if len(types) == 0:
                    raise Exception("Cannot find said movie type")
                elif warnme != len(types_to_show[0]): raise Exception("Cannot find said movie type")
                else:contin = 1
            else: contin = 1

            if contin == 1:
                main_content["showings"].clear()
                for i in types:
                    main_content["showings"].update(i)





        # ═════════════════CINEMAS FILTER════════════════
        if isinstance(cinemas_to_show, str):
            cinemas_to_show = ([cinemas_to_show], True)
        elif isinstance(cinemas_to_show, list):
            cinemas_to_show = (cinemas_to_show, True)
        elif isinstance(cinemas_to_show, tuple):
            if isinstance(cinemas_to_show[0], str):
                cinemas_to_show = ([cinemas_to_show[0]], cinemas_to_show[1])
            elif isinstance(cinemas_to_show[0], list):
                cinemas_to_show = (cinemas_to_show[0], cinemas_to_show[1])

        if not isinstance(cinemas_to_show[1], bool):
            raise Exception("cinemas_to_show second argument should be a boolean")

        if str(cinemas_to_show[0][0]).lower() != "all":
            contin = 0
            new_showings = []
            warnme = 0

            for key, value in main_content["showings"].items():
                for cinemas in cinemas_to_show[0]:
                    if jellyfish.jaro_winkler_similarity(re.sub('[^A-Za-z0-9]+', '', key.lower()), re.sub('[^A-Za-z0-9]+', '', re.sub('[^A-Za-z0-9]+', '', str(cinemas).lower()))) > 0.84:
                        new_showings.append({key: value})
                        warnme+=1

            if cinemas_to_show[1]:
                if len(new_showings) == 0:
                    raise Exception("Cannot find said cinema")
                elif len(cinemas_to_show[0]) != warnme: raise Exception("Cannot find said cinema")
                else:contin = 1
            else: contin = 1

            if contin == 1:
                main_content["showings"].clear()
                for i in new_showings:
                    main_content["showings"].update(i)

        # ═════════════════EMIRATES FILTER════════════════
        if isinstance(emirates_to_show, str) or emirates_to_show is None:
            emirates_to_show = (emirates_to_show, True)

        if isinstance(emirates_to_show, list):
            emirates_to_show = (emirates_to_show, True)
        if isinstance(emirates_to_show, tuple):
            if isinstance(emirates_to_show[0], str):
                emirates_to_show = ([emirates_to_show[0]], emirates_to_show[1])
            elif isinstance(emirates_to_show[0], list):
                emirates_to_show = (emirates_to_show[0], emirates_to_show[1])

        if not isinstance(emirates_to_show[1], bool):
            raise Exception("emirates_to_show second argument should be a boolean")

        if not emirates_to_show[0] is None:
            cinema_names = list(main_content["showings"].keys())

            for __, _ in enumerate(cinema_names):
                main_content["showings"][self.location_cinema(_)] = {}
            for ol, _ in enumerate(cinema_names):
                main_content["showings"][self.location_cinema(_)][cinema_names[ol]] = {}
            for ol, _ in enumerate(cinema_names):
                main_content["showings"][self.location_cinema(_)][cinema_names[ol]].update(main_content["showings"].pop(cinema_names[ol]))

            if str(emirates_to_show[0][0]).lower() != "all":
                contin = 0
                new_showings = []
                warnme = 0

                for key, value in main_content["showings"].items():
                    for emirates in emirates_to_show[0]:
                        if jellyfish.jaro_winkler_similarity(re.sub('[^A-Za-z0-9]+', '', key.lower()),
                                                             re.sub('[^A-Za-z0-9]+', '', re.sub('[^A-Za-z0-9]+', '',
                                                                                                str(emirates).lower()))) > 0.85:
                            new_showings.append({key: value})
                            warnme += 1

                if emirates_to_show[1]:
                    if len(new_showings) == 0:
                        raise Exception("Cannot find said emirate")
                    elif len(emirates_to_show[0]) != warnme:
                        raise Exception("Cannot find said emirate")
                    else:
                        contin = 1
                else:
                    contin = 1


                if contin ==1:
                    main_content["showings"].clear()
                    for i in new_showings:
                        main_content["showings"].update(i)




        return main_content


    def get_all_whatson_movies_info_timings(self,
                    threads:int = 1,
                    delay: int | float = 0,
                    day: str | int = "today",
                    types_to_show: tuple | str | list = ("all", True),
                    cinemas_to_show: tuple | str | list = ("all", True),
                    emirates_to_show: tuple | str | list | None = ("all", True),
                    tmdb: bool = False,
                    imdb: bool = False):
        time.sleep(delay)
        return ThreadPool(threads).map(lambda x: self.sheeeeeeesh(x,
                                                                  day,
                                                                  types_to_show,
                                                                  cinemas_to_show,
                                                                  emirates_to_show,
                                                                  tmdb,
                                                                  imdb), (self.whatson_links()))
