#!/usr/bin/env python
"""Convert Librarything JSON export to microformat md files"""
import json
import os.path
import sys
from slugify import slugify

BAD_ENDINGS = (
    "(Abacus Books)", "(Big)", "(Bk.1)", "(Blackwell Manifestos)",
    "(Blackwell Readers)", "(Canongate Classics)", "(Cape poetry)",
    "(Cape Poetry)", "(Carcanet Fiction)", "(Classics)",
    "(Comix)", "(Contemporary American Fiction)", "(Deluxe Edition)",
    "(Dent Everyman\"s Library)", "(Duck Series)", "(E)",
    "(Essential Penguin)", "(Everyman Poetry)", "(Everyman's Library)",
    "(Faber poetry)", "(Felix Pollak Prize in Poetry)", "(Fiction series)",
    "(Five Star Paperback)", "(flamingo)", "(Flamingo modern classics)",
    "(FSG Classics)", "(Gallery Books)", "(golden compass)",
    "(Golden Compass)", "(Grove Press Poetry)", "(Harvest Book)",
    "(Harvill Panther)", "(Houghton Library Publications)", "(King Penguin)",
    "(King Penguin S.)", "(Mermaid Books)", "(New Directions Paperbook)",
    "(New Directions Pearls)", "(New Oxford Illustrated Dickens)",
    "(New York Review Books)", "(New York Review Books Classics)",
    "(New York Review Books Children's Collection)", "(Flamingo)",
    "(None)", "(NYRB Classics)", "(Oxford Paperback Reference)",
    "(Oxford Paperbacks)", "(Oxford poets)", "(Oxford Poets)",
    "(Oxford Poets series)", "(Oxford World&#039;s Classics)",
    "(Paladin Books)", "(Panther)", "(Pelican)", "(Penguin Classics)",
    "(Penguin Classics Deluxe Edition)", "(Penguin Drop Caps)",
    "(Penguin Graphic Fiction)", "(Penguin Great Ideas)", "(Penguin History)",
    "(Penguin International Poets)", "(Penguin International Writers)",
    "(penguin modern classics)", "(Penguin Modern Classics)",
    "(Penguin Originals)", "(Penguin Poetry)", "(Alabama poetry series)",
    "(penguin twentieth century classics)", "(Cookery Library)",
    "(penguin twentieth-century classics)", "(Social Science Paperbacks)",
    "(Penguin Twentieth Century Classics)", "(v. 2)", "[Paperback]",
    "(Penguin Twentieth-Century Classics)", "(SIGNED)", "(v. 1)",
    "(Perspectives)", "(Peter Owen Modern Classics)",
    "(Phoenix Fiction Series)", "(Phoenix Poets)", "(Picador)",
    "(picador books)", "(Picador Books)", "(Pimlico)",
    "(Pitt Poetry Series)", "(Plain)", "(Poetry Book Society Recommendation)",
    "(Poetry Pleiade)", "(Poets)", "(Poets, Penguin)",
    "(Prairie Schooner Book Prize in Poetry)",
    "(P.S.)", "(Pushkin paper)", "( \" Rebel Inc. \" Classics)",
    "(Salt Modern Poets S.)", "(Seagull Books - Seagull World Literature)",
    "(Seagull Books - The Africa List)", "(Southern Messenger Poets Series)",
    "[issue, #, number, no., seven, VII] (SIGNED)", "(Spanish Edition)",
    "(Swenson Poetry Award)", "(The Art of the Novella)",
    "(The Art of the Novella series)", "(The Contemporary Art of the Novella)",
    "(Tin House New Voice)", "(Triquarterly Books)", "(UK edition)",
    "(Utterly Confused Series)", "(Verba Mundi)", "(Vintage)",
    "(Vintage Classics)", "(Vintage Contemporaries)",
    "(Vintage Contemporaries Original)", "(Vintage International)",
    "(Wessex Editions)", "(Yale Series of Younger Poets)",
    "(Zed New Fiction)"
)
# PATH='library'
EXTRA = 'extra'


def get_book_details(book):
    """Get book details."""
    publisher, bookformat, pages = get_publication(book)
    return {
        'publisher': publisher,
        'format': bookformat,
        'pages': pages,
        'date': book['date'],
        'authors': get_authors(book),
        'language': get_language(book),
        'awards': get_awards(book),
        'ddc': get_ddc(book),
        'lcc': get_lcc(book),
        'tags': get_tags(book),
    }


def get_isbn(book):
    """get isbn"""
    isbn = book.get('isbn')
    if isbn:
        isbn = isbn['2'] if isinstance(isbn, dict) else isbn[0]
    return isbn


def get_title(book):
    """Get book title."""
    title = book['title'].encode('utf-8')
    bad = False
    if title == title.upper():
        title = title.title()
        if len(title.split()) > 2:
            bad = True
    if title.endswith(BAD_ENDINGS):
        title = title.split('(')[0]
    if title == title.capitalize() and len(title.split()) > 1:
        title = title.title()
        if len(title.split()) > 2:
            bad = True
    return title, bad


def get_page_name(isbn, title):
    """Get name of output file."""
    if isbn:
        page_name = isbn
    else:
        isbn = 'None'
        page_name = slugify(title)
    return page_name + '.md'


def get_authors(book):
    """Get Author section"""
    author_formatstr = "  <span class='p-author {} h-card'>{}</span><br>\n"
    authors = ''
    if len(book['authors'][0]) > 0:
        for author in enumerate(book['authors']):
            if author[0] == 0:
                p_role = 'p-primaryauthor'
                role = None
            elif 'role' in author[1]:
                role = author[1]['role']
                p_role = 'p-' + role
            else:
                p_role = 'p-secondaryauthor'
                role = None
            if role:
                authors += " {}:".format(role)
            authors += author_formatstr.format(
                p_role, author[1]['fl'].encode('utf-8').title()
            )
    elif 'primaryauthor' in book:
        authors += author_formatstr.format(
            'p-primaryauthor', book['primaryauthor'].encode('utf-8').title()
        )
    if authors:
        fmtstr = "<p class='h-authors'>\n{}</p>\n"
        authors = fmtstr.format(authors)
    return authors


def get_awards(book):
    """Get awards."""
    awards = book.get('awards')
    if awards:
        awards = ",\n".join([
            "<span class='p-award'>{}</span>".format(
                award.encode('utf-8')
            ) for award in awards
        ])
        fmtstr = "<br><span class='h-awards'>{}</br>\n"
        awards = fmtstr.format(awards)
    return awards


def get_ddc(book):
    """Get Dewey Decimal Classification"""
    ddc = book.get('ddc')
    if ddc:
        ddcstr = (
            "<br><span class='h-ddc' rel='category'>\n"
            "Dewey Decimal: <span class='p-code'>{}</span>\n"
        )
        ddcstr = ddcstr.format(ddc['code'][0])
        wording = ddc.get('wording')
        if wording:
            wording = [
                "<span class='p-wording'>{}</span>".format(
                    word.encode('utf-8')
                ) for word in wording
            ]
            wording = ",\n".join(wording)
            ddcstr = "{}{}{}".format(ddcstr, "<br>", wording)
        ddc = "{}</span>".format(ddcstr)
    return ddc


def get_language(book):
    """Get language data."""
    langstr = ''
    if 'language' in book:
        fmtstr = "<br>Language: <span class='p-language'>{}</span>\n"
        langstr += fmtstr.format(", ".join(book['language']))
    originallanguage = book.get('originallanguage')[0]
    if originallanguage and originallanguage != 'English'\
            and originallanguage != '(blank)':
        fmtstr = (
            "<br> Original Language: "
            "<span class='p-originallanguage'>{}</span>\n"
        )
        langstr += fmtstr.format(originallanguage)
    return langstr


def get_lcc(book):
    """Get LCC Call No"""
    lcc = book.get('lcc')
    if lcc:
        fmtstr = ("LCC: <span class='p-lcc' rel='category'>{}</span>\n")
        lcc = fmtstr.format(book['lcc']['code'])
    return lcc


def get_publication(book):
    """Get publisher, pagecount and format, checking for common bad cases"""
    pub = book['publication'].split(',')
    publisher = pub[0].partition('(')[0].strip()
    if publisher.isupper():
        publisher = publisher.title()
    bookformat = book.get('format')
    if bookformat:
        bookformat = bookformat[0].get("text")
    else:
        pubformat = pub[len(pub) - 2].lstrip()
        if not (pubformat.startswith(publisher) or
                pubformat.startswith('(') or
                pubformat[:1].isdigit()):
            bookformat = pubformat
    if bookformat and bookformat.isupper():
        bookformat = bookformat.title()
    pages = book.get('pages')
    if not pages:
        pages = pub[len(pub) - 1].strip(' pages')
    return publisher, bookformat, pages.rstrip()


def get_tags(book):
    """add tags to books"""
    tags = []
    if 'subject' in book:
        subj = book['subject']
        if isinstance(subj, dict):
            for subjectlist in subj.itervalues():
                tags.extend(subjectlist)
        else:
            for subjectlist in subj:
                tags.extend(subjectlist)

    if 'tags' in book:
        tags.extend(book['tags'])
    if tags:
        tags = set(tags)
        tags.discard(None)
        tags = ", ".join(
            ['#' + tag.encode('utf-8') for tag in tags]
        )
    return tags


def get_supplement(filename):
    """Retrieve contents to be added to file"""
    filepath = os.path.join(EXTRA, filename)
    supplement = None
    if os.path.exists(filepath):
        with open(filepath, 'r') as extra:
            supplement = extra.readlines()
            supplement = ['\n', '\n'] + supplement
    return supplement


def get_command_line_args():
    """Get command line args."""
    mdpath = ''
    inputfile = 'librarything_tallpaul.json'
    try:
        inputfile = sys.argv[1]
        mdpath = sys.argv[2]
    except IndexError:
        pass
    return inputfile, mdpath


def main():
    """Main."""
    inputfile, mdpath = get_command_line_args()
    with open(inputfile, 'r') as ltdump:
        data = json.load(ltdump)
        for book in data.itervalues():
            isbn = get_isbn(book)
            title, isbad = get_title(book)
            page_name = get_page_name(isbn, title)
            print title, page_name
            file_path = os.path.join(mdpath, page_name)
            if isbad:
                print "bad title in {}".format(file_path)
            book = get_book_details(book)
            supplement = get_supplement(page_name)

            with open(file_path, 'w') as mdfile:
                mdfile.write("<div class='h-item book'>\n")

                fmtstr = "<h2 class='p-name booktitle'>{}</h2>\n"
                mdfile.write(fmtstr.format(title))
                mdfile.write(book['authors'])

                mdfile.write("<p class='h-publication'>\n")

                fmtstr = "  <span class='p-brand p-publisher'>{}</span>\n"
                mdfile.write(fmtstr.format(book['publisher']))

                fmtstr = "  <span class='dt-date'>{}</span><br>\n"
                mdfile.write(fmtstr.format(book['date']))

                if book.get('format'):
                    fmtstr = "  <span class='p-format'>{}</span>, "
                    mdfile.write(fmtstr.format(book['format']))

                fmtstr = "  <span class='p-pages'>{}</span> pages<br>\n"
                mdfile.write(fmtstr.format(book['pages']))

                fmtstr = "  ISBN: <span class='u-uid p-isbn2'>{}</span><br>\n"
                mdfile.write(fmtstr.format(isbn))
                mdfile.write("</p>\n")

                if book.get('lcc') or book.get('ddc'):
                    mdfile.write("<p class='h-catalog'>\n")
                    if book.get('lcc'):
                        mdfile.write(book['lcc'])
                    if book.get('ddc'):
                        mdfile.write(book['ddc'])
                    mdfile.write("</p>\n")

                if book.get('language'):
                    mdfile.write(book['language'])
                if book.get('awards'):
                    mdfile.write(book['awards'])
                mdfile.write("</div>\n")

                if book.get('tags'):
                    mdfile.write(
                        "<p span='p-category'>{}</p>".format(book['tags'])
                    )

                if supplement:
                    mdfile.writelines(supplement)


if __name__ == "__main__":
    main()
