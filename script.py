from yattag import Doc
from collections import defaultdict
import fileinput

class Conference:
    def __init__(self, line):
        self.lower_name, self.name_topic = line.split(', ')
        self.upper_name= self.name_topic.split(' ')[0]
        self.papers = []

class Paper:
    def __init__(self, line):
        splits = line.split(', ')
        self.year, self.url = splits[0], splits[1]
        self.title = ",".join(splits[2:])
        if len(self.title) > 99:
            self.title = self.title[:99] + '...'
        self.authors = []
    
    def get_last_name_of_first_author(self):
        return self.authors[0].name.split(' ')[-1]
    
    def get_url(self):
        if self.url:
            return self.url
        return "http://scholar.google.com/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq={}&as_oq=&as_eq=&as_occt=any&as_sauthors={}".format(self.title, self.get_last_name_of_first_author())

class Author:
    def __init__(self, line):
        self.name, self.institution = line[2:].split(', ')

def get_parsed_conferences():
    conferences = []
    conference = None
    paper = None
    author = None
    paper_year_count = defaultdict(dict)

    for line in fileinput.input():
        line = line.rstrip()
        if not line.startswith(" "):
            #neurips, NeurIPS (Machine Learning)
            if conference is None:
                conference = Conference(line)
            else:
                # Add the current paper to the current conference
                conference.papers.append(paper)
                conferences.append(conference)
                conference = Conference(line)
                paper = None
            paper_year_count[conference.lower_name] = defaultdict(int)
        elif line.startswith("  "):
            #  Ilias Diakonikolas, University of Southern California
            author = Author(line)
            paper.authors.append(author)
        else:
            # 2019, , Distribution-Independent PAC Learning of Halfspaces with Massart Noise
            if paper is not None:
                conference.papers.append(paper)
            paper = Paper(line)
            paper_year_count[conference.lower_name][paper.year] += 1
    conferences.append(conference)

    conferences = sorted(conferences, key=lambda x : x.lower_name)
    for conference in conferences:
        conference.papers = sorted(conference.papers, key = lambda paper: paper.year, reverse=True)
    return conferences, paper_year_count

def get_sorted_institution_scores(conferences):
    total_institution_scores = defaultdict(int)
    for conference in conferences:
        for paper in conference.papers:
            total_sum = 0
            institution_scores = defaultdict(int)
            for author_index, author in enumerate(paper.authors):
                institution_scores[author.institution] += 1/(author_index + 1)
                total_sum += 1/(author_index + 1)
            for institution in institution_scores:
                total_institution_scores[institution] += (institution_scores[institution] / total_sum)
    filtered_scores = dict(filter(lambda item: item[1] >= 2, total_institution_scores.items()))
    sorted_scores = {institution: round(score, 1) for institution, score in sorted(filtered_scores.items(), key=lambda item: item[1], reverse=True)}
    return sorted_scores

def build_doc(conferences, paper_year_count):
    doc, tag, text = Doc().tagtext()

    doc.asis('<!DOCTYPE html>')
    with tag('html', lang="en"):
        with tag('head'):
            doc.stag('meta', name="description", content="Best paper awards (since 1996) for top-tier computer science conferences: {conference_list}.")
            doc.stag('meta', ("http-equiv", "Content-Type"), ("content", "text/html;charset=utf-8"))
            with tag('title'):
                text('Best paper awards at {conference_list}')
            doc.asis("""<style type="text/css">body{font-family:sans-serif;font-size:13px}li{margin:5px 0 8px 0}a{text-decoration:none}h1{font-size:1.6em}""" \
                    """table{font-size:13px;border-width:1px;border-spacing:0;border-style:none;border-color:grey;border-collapse:collapse}""" \
                    """table td{border-width:1px;padding:2px 4px;border-style:solid;border-color:grey}thead td{text-align:center;font-weight:700;font-size:1.7em;background-color:#eee}""" \
                    """div{display:none}</style>""")
        with tag('body'):
            with tag('h1'):
                text('Best Paper Awards in Computer Science (since 1996)')
            with tag('p'):
                text('By Conference:')
                with tag('b'):
                    doc.asis(' &nbsp; ')
                    for conference in conferences:
                        with tag('a', href="#{}".format(conference.lower_name)):
                            text(conference.upper_name)
                        doc.asis(' &nbsp; ')
            with tag('p'):
                with tag('b'):
                    with tag('a', href="#institutions"):
                        text('Institutions with the most Best Papers')
            with tag('p'):
                text("""Much of this data was entered by hand (obtained by contacting past conference organizers, retrieving cached
            conference websites, and searching CVs) so please email me if you notice any errors or omissions:
            bestpaper-AT-jeffhuang.com. I (Jeff Huang) tried to collect best paper awards from the top-tier conferences in
            each area, but some conferences do not have such an award (e.g. SIGGRAPH, CAV). "Distinguished paper award" and
            "outstanding paper award" are included but not "best student paper" (e.g. NIPS) or "best 10-year old paper"
            (e.g. POPL). The list of papers for years 2017 and 2018 were collected by Mingrui Ray Zhang.""")
            with tag('table'):
                for conference in conferences:
                    with tag('thead'):
                        with tag('td', colspan=3):
                            with tag('a', name=conference.lower_name):
                                text(conference.name_topic)
                    for paper in conference.papers:
                        with tag('tr'):
                            if paper_year_count[conference.lower_name][paper.year]:
                                with tag('td', rowspan=paper_year_count[conference.lower_name][paper.year]):
                                    with tag('b'):
                                        text(paper.year)
                                del paper_year_count[conference.lower_name][paper.year]
                            with tag('td'):
                                with tag('a', href=paper.get_url()):
                                    text(paper.title)
                            with tag('td'):
                                if len(paper.authors) == 2:
                                    if paper.authors[0].institution == paper.authors[1].institution:
                                        doc.asis('{author1} & {author2}, {institution}'.format(author1=paper.authors[0].name, author2=paper.authors[1].name, institution=paper.authors[0].institution))
                                    else:
                                        doc.asis('{author}, {institution}'.format(author=paper.authors[0].name, institution=paper.authors[0].institution))
                                        doc.stag('br')
                                        doc.asis('{author}, {institution}'.format(author=paper.authors[1].name, institution=paper.authors[1].institution))
                                else:
                                    doc.asis('{author}, {institution}'.format(author=paper.authors[0].name, institution=paper.authors[0].institution))
                                    if len(paper.authors) == 1:
                                        continue
                                    with tag('a', href="#", onclick="this.nextSibling.style.display = 'block'; this.style.display = 'none'; return false;"):
                                        text('; et  al.')
                                    with tag('div'):
                                        for author in paper.authors[2:]:
                                            doc.asis(author.name + ", " + author.institution)
                                            doc.stag('br')
            doc.stag('br')
            doc.stag('br')
            with tag('table'):
                with tag('thead'):
                    with tag('td', colspan=2):
                        with tag('a', name="institutions"):
                            text('Institutions with Best Papers')
                for institution, score in sorted_scores.items():
                    with tag('tr'):
                        with tag('td'):
                            doc.asis(institution)
                        with tag('td'):
                            text(score)
        doc.asis("""
        <p>Credit is given in decreasing author order as customary in many fields. First authors are given 1 point, second
            authors are given 0.5 points, third authors are given 0.33 points, etc. These points are then divided by the sum
            of points for that paper, i.e. normalizing it. This ranking may be inaccurate or incomplete, may not reflect the
            current state of best paper awards, and is not an official list. If you are not satisfied with the ranking
            listed here, please disregard it.</p>
        <p>Back to <a href="https://jeffhuang.com/">Jeff Huang's Homepage</a></p>
        <p><a href="http://hci.cs.brown.edu">Brown University Human-Computer Interaction Research Group</a></p><br>
        <p>
            <font color="gray">Page last updated: 2019-02-21</font>
        </p>""")
    return doc

if __name__ == '__main__':
    conferences, paper_year_count = get_parsed_conferences()
    sorted_scores = get_sorted_institution_scores(conferences)
    conference_list = ", ".join(list(map(lambda x: x.upper_name, conferences)))
    doc = build_doc(conferences, paper_year_count)
    print(doc.getvalue().replace("{conference_list}", conference_list))