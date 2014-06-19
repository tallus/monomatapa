"""Filters for jinja 2"""
# Conversion Constants
H_VALS = [
    'adr',
    'card',
    'event',
    'entry',
    'geo',
    'item',
    'product',
    'recipe',
    'resume',
    'review',
    'review-aggregate'
]

DT_VALS = [
    'anniversary',
    'bday',
    'duration',
    'end',
    'published',
    'reviewed',
    'start',
    'update'
]
	
P_VALS = [
    'additional-name',
    'adr',
    'affiliation',
    'altitude',
    'author',
    'best',
    'brand',
    'category',
    'contact',
    'count',
    'country-name',
    'education',
    'experience',
    'extended-address',
    'family-name',
    'gender-identity',
    'geo',
    'given-name',
    'honorific-prefix',
    'honorific-suffix',
    'ingredient',
    'item',
    'job-title',
    'label',
    'latitude',
    'locality',
    'location',
    'longitude',
    'name',
    'nickname',
    'nutrition',
    'note',
    'org',
    'post-office-box',
    'postal-code',
    'price',
    'rating',
    'region',
    'review',
    'reviewer',
    'role',
    'sex',
    'skill',
    'sort-string',
    'street-address',
    'summary',
    'tel',
    'votes',
    'worst',
    'yield'
]


E_VALS =  [
    'content',
    'description',
    'instructions'
]

U_VALS = [
    'email',
    'impp',
    'key',
    'logo',
    'photo',
    'uid',
    'url'
  ]

CONVERT = {'address' : 'h-adr'}

@app.template_filter('h-render')
def h_render(struct):
    """filter that renders an h-card or similar. 
    
    

    The badly named struct is a list of lists of dicts (and strings) like so:
    card [{name: value}, {name: {name : [name, name], value : value, url: url}}, string,
    {name :[ {name: value}, ...]
    Refer to h-card.template for what it actually should look like.

    It gets rendered like this:
    <div class="h-card">
        <span class=name>value</string>
        <span class="name name", href=url>value</span>a string
        <div class="name">
            <span class=name>value</string>
        </div>
    </div>
    """
    pass
