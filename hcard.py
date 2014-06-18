from mf2py.parser import Parser
hcard = '''
<div id="hcard-Paul-Munday" class="hcard">
 <a class="u-url p-name" href="http://paulmunday.net">Paul Munday</a>
 <div class="p-org">The Invisible College</div>
 <a class="u-email" href="mailto:paul@paulmunday.net">paul@paulmunday.net</a>
 <div class="h-adr">
  <div class="p-post-office-box">PO Box 28228</div>
  <div class="p-street-address">3531 SE 11th Ave</div>
  <span class="p-locality">Portland</span>
, 
  <span class="p-region">OR</span>
, 
  <span class="p-postal-code">97202</span>

  <span class="p-country-name">USA</span>

 </div>
 <div class="p-tel">503-318-8922</div>
</div>
'''
p = Parser(doc=hcard)
js = p.to_json()
print js
