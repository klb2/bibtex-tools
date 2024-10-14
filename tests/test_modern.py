import pytest

import bibtexparser
from bibtexparser.bparser import BibTexParser

from bibtextools import modernize_bib_file
from bibtextools.const import KEY_ENTRYTYPE


BIB_MAIN = "old.bib"

def test_main_modern(bib_file=BIB_MAIN):
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file)
    assert len(clean_entries) == 6

def test_replace_id(bib_file=BIB_MAIN):
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file, replace_ids=True)
    expected_keys = set(["Name2010title", "MultipleWordName2010title",
                         "Jorswieck2020copula", "Duck2018ecg",
                         "AuthorwithLastNames2015title", "Report2005"])
    cleaned_keys = set([k[modernize_bib_file.KEY_ID]
                        for k in clean_entries])
    assert cleaned_keys == expected_keys

def test_arxiv_primaryclass(bib_file=BIB_MAIN):
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file, arxiv=True)
    _entry = [k for k in clean_entries
              if k[modernize_bib_file.KEY_ID] == "Besser2020CLpart1"][0]
    assert _entry[modernize_bib_file.KEY_CATEGORY] == "cs.IT"

def test_journal_abbreviation(bib_file=BIB_MAIN):
    from bibtextools.util import load_bib_file
    abbr_expectation = {"Journal Title": "J. Title",
                        "Title of the Journal": "J. Title",
                        "{IEEE} Communications Letters": "{IEEE} Commun. Lett.",
                       }
    dirty_entries = load_bib_file(bib_file).get_entry_dict()
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file, iso4=True)
    _correct = []
    for _entry in clean_entries:
        if not any(_key in _entry for _key in modernize_bib_file.KEYS_JOURNAL):
            _correct.append(_entry == dirty_entries[_entry[modernize_bib_file.KEY_ID]])
        else:
            for _key in modernize_bib_file.KEYS_JOURNAL:
                if _key in _entry:
                    _correct.append(_entry[_key] == abbr_expectation[dirty_entries[_entry[modernize_bib_file.KEY_ID]]])
    print(_correct)
    assert all(_correct)

def test_author_getnames():
    old_names = ["Last, First", "{van Name}, First", "{One Single Name}",
                 "First {di Last Name}", "von Name, First", "CompanyName",
                 r'Ludger R{\"{u}}schendorf']
    expected = ["Last, First", "{van Name}, First", "{One Single Name}",
                "{di Last Name}, First", "von Name, First", "CompanyName",
                r'R{\"{u}}schendorf, Ludger']
    new_names = modernize_bib_file.getnames(old_names)
    print(old_names)
    print(new_names)
    assert new_names == expected

@pytest.mark.parametrize("title,expected",
                         [("MIMO", r"{MIMO}"), ("M2M", r"{M2M}"),
                          (r"Acro IN mmWave Title", r"Acro {IN} {mmWave} Title"),
                          (r"Math $\mu=\alpha$", r"Math {$\mu=\alpha$}"),
                          (r"Already {ACRO} in", r"Already {ACRO} in"),
                          (r"{Surrounding {ACRO}}", r"Surrounding {ACRO}"),
                          (r"5G should be SHIELded", r"{5G} should be {SHIELded}"),
                          (r"Regular title with Names", r'Regular title with Names'),
                         ])
def test_title_shielding_acronyms(title, expected):
    cleaned = modernize_bib_file.clean_title(title)
    assert cleaned == expected

@pytest.mark.parametrize("title,expected",
                         [("MIMO", r"{{MIMO}}"), ("M2M", r"{{M2M}}"),
                          (r"{MIMO}", r"{MIMO}"), (r"{M2M}", r"{M2M}"),
                          (r"Acro IN mmWave Title", r"{Acro {IN} {mmWave} Title}"),
                          (r"Math $\mu=\alpha$", r"{Math {$\mu=\alpha$}}"),
                          (r"Already {ACRO} in", r"{Already {ACRO} in}"),
                          (r"{Surrounding {ACRO}}", r"{Surrounding {ACRO}}"),
                          (r"{All in curly}", r"{All in curly}"),
                          (r"Regular title with Names", r'{Regular title with Names}'),
                         ])
def test_title_shielding(title, expected):
    cleaned = modernize_bib_file.clean_title(title, shield_title=True)
    assert cleaned == expected

@pytest.mark.parametrize("title,expected",
                         [
("Journal of Polymer Science Part A", "J. Polym. Sci. A"),
("Proceedings of the Institution of Mechanical Engineers, Part A", "Proc. Inst. Mech. Eng. A"),
("Bulletin of the Section of Logic", "Bull. Sect. Log."),
("The Lancet", "Lancet"),
("Baha'i Studies Review", "Baha'i Stud. Rev."),
("Journal of Shi'a Islamic Studies", "J. Shi'a Islam. Stud."),
("The Mariner's Mirror", "Mar. Mirror"),
("The Mechanics' Institute Review", "Mech. Inst. Rev."),
("Journal of Children's Orthopaedics", "J. Child. Orthop."),
("Annali dell'Istituto Superiore di Sanità", "Ann. Ist. Super. Sanità"),
("In Practice", "In Practice"),
("In the Library with the Lead Pipe", "In Libr. Lead Pipe"),
("Off our backs", "Off our backs"),
("Volume!", "Volume!"),
("Australasian Journal of Educational Technology", "Australas. J. Educ. Technol."),
("Real-World Economics Review", "Real-World Econ. Rev."),
("Real Analysis Exchange", "Real Anal. Exch."),
("Annals of Clinical & Laboratory Science", "Ann. Clin. Lab. Sci."),
("Journal of Early Christian Studies", "J. Early Christ. Stud."),
("Journal of Crustacean Biology", "J. Crustac. Biol."),
("Carniflora Australis", "Carniflora Aust."),
("Humana.Mente", "Humana.Mente"),
("Spunti e ricerche", "Spunti ric."),
("Journal of Chemical Physics A", "J. Chem. Phys. A"),
("Revista Médica de Chile", "Rev. Méd. Chile"),
("Romanian Journal of Physics", "Rom. J. Phys."),
("Journal de Théorie des Nombres de Bordeaux", "J. Théor. Nr. Bordx."),
("Labor History", "Labor Hist."),
("Archiv Orientální", "Arch. Orient."),
("Ślaski Kwartalnik Historyczny Sobótka", "Śl. Kwart. Hist. Sobótka"),
("Mitteilungen der Österreichischen Geographischen Gesellschaft", "Mitt. Österr. Geogr. Ges."),
("Filosofický časopis", "Filos. čas."),
("Cahiers québécois de démographie", "Cah. qué. démogr."),
("Análisis Filosófico", "Anál. Filos."),
("Inorganica Chimica Acta", "Inorg. Chim. Acta"),
("Comptes rendus de l'Académie des Sciences", "C. r. Acad. Sci."),
("Proceedings of the National Academy of Sciences of the United States of America", "Proc. Natl. Acad. Sci. U. S. A."),
("Scando-Slavica", "Scando-Slav."),
("Zeitschrift des Deutschen Palästina-Vereins", "Z. Dtsch. Paläst.-Ver."),
("International Journal of e-Collaboration", "Int. J. e-Collab."),
("Proceedings of A. Razmadze Mathematical Institute", "Proc. A. Razmadze Math. Inst."),
("Norsk Militært Tidsskrift", "Nor. Mil. Tidsskr."),
                          ])
def test_journal_abbreviation(title, expected):
    entry = {"journal": title, KEY_ENTRYTYPE: "article"}
    entry = modernize_bib_file.abbreviate_journalname(entry)
    abbr_title = entry['journal']
    assert abbr_title == expected

# Not used due to bug in pyiso4:
# https://github.com/pierre-24/pyiso4/issues/11
#@pytest.mark.parametrize("title,expected",
#                         [
#("J. Polym. Sci. A", "J. Polym. Sci. A"),
#("Proc. Inst. Mech. Eng. A", "Proc. Inst. Mech. Eng. A"),
#("Nor. Mil. Tidsskr.", "Nor. Mil. Tidsskr."),
#("IEEE Trans. on Wireless Communications", "IEEE Trans. Wirel. Commun."),
#                          ])
#def test_existing_journal_abbreviation(title, expected):
#    entry = {"journal": title, KEY_ENTRYTYPE: "article"}
#    entry = modernize_bib_file.abbreviate_journalname(entry)
#    abbr_title = entry['journal']
#    assert abbr_title == expected
