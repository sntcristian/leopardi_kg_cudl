from lxml import etree
import glob
import json

def parse_tei(xml_file_path):
    ns = {'tei': 'http://www.tei-c.org/ns/1.0', "xml":"http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(xml_file_path)
    root = tree.getroot()

    repository = root.find('.//tei:msIdentifier/tei:repository', namespaces=ns).text
    id_doc = root.find('.//tei:msIdentifier/tei:idno', namespaces=ns).text

    # Use the namespace in the XPath query and access title
    title = root.find('.//tei:msItem/tei:title', namespaces=ns).text

    lang = root.find('.//tei:msItem/tei:textLang', namespaces=ns).text

    # Find support information and extent
    support = " ".join([t.strip() for t in root.find('.//tei:supportDesc/tei:support', namespaces=ns).itertext()])
    extent = root.find('.//tei:supportDesc/tei:extent', namespaces=ns).text
    
    # Find origin date and place
    orig_date = root.find('.//tei:origin/tei:origDate', namespaces=ns).text
    orig_place = root.find('.//tei:origin/tei:origPlace', namespaces=ns)
    orig_place_key = orig_place.get("key")
    orig_place_text = orig_place.text
    
    # Find list of persons in letter and viaf key
    persons = root.findall('.//tei:listPerson/tei:person', namespaces=ns)
    pers_list = []
    for person in persons:
        ref = person.get("{http://www.w3.org/XML/1998/namespace}id")
        key = person.find("tei:persName", namespaces=ns).get("key")
        forename = person.find("tei:persName/tei:forename", namespaces=ns).text
        surname = person.find("tei:persName/tei:surname", namespaces=ns).text
        pers_list.append({"key":key, "ref":ref, "forename":forename, "surname":surname, "persName":forename+" "+surname})
    
    # Find list of places in letter and GeoNames key
    places = root.findall('.//tei:listPlace/tei:place', namespaces=ns)
    place_list = []
    for place in places:
        ref = place.get("{http://www.w3.org/XML/1998/namespace}id")
        key = place.find("tei:placeName", namespaces=ns).get("key")
        name = place.find("tei:placeName", namespaces=ns).text
        place_list.append({"key":key, "ref":ref, "placeName":name})

    
    # Extract correspondents
    correspondents = root.findall('.//tei:correspDesc/tei:correspAction', namespaces=ns)
    for correspondent in correspondents:
        if correspondent.get("type")=="sent":
            sender_name = correspondent.find("tei:persName", namespaces=ns).text
            sender_key = correspondent.find("tei:persName", namespaces=ns).get("key")
        if correspondent.get("type")=="received":
            receiver_name = correspondent.find("tei:persName", namespaces=ns).text
            receiver_key = correspondent.find("tei:persName", namespaces=ns).get("key") 
    try:
        sender = sender_name+" ("+sender_key+")"
        receiver = receiver_name+" ("+receiver_key+")" 
    except:
        sender = ""
        receiver=""

    doc_txt = " ".join([t.strip() for t in root.find('.//tei:text/tei:body', namespaces=ns).itertext()])
    output = {"id_doc":id_doc, 
              "repo":repository, 
              "title":title,
              "lang":lang,
              "support":support,
              "extent":extent,
              "orig_date":orig_date,
              "orig_place":orig_place_text + " ("+orig_place_key+")",
              "sender": sender,
              "receiver":receiver,
              "text":doc_txt,
              "persons":pers_list,
              "places":place_list
            }
    return output

lst_of_dict = []
for tei_doc in glob.glob("xml_tei/*.txt"):
    xml_file_path = tei_doc
    parsed_file = parse_tei(xml_file_path)
    lst_of_dict.append(parsed_file)


with open("test.json", "w", encoding="utf-8") as f:
    json.dump(lst_of_dict, f, ensure_ascii=False, indent=4)