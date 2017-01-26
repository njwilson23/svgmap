import xml.etree.ElementTree as ET

def _xml_element_equal(el1, el2):
    if el1.tag != el2.tag:
        return False
    if el1.attrib != el2.attrib:
        return False
    children1 = el1.getchildren()
    children2 = el2.getchildren()
    if len(children1) != len(children2):
        return False
    for child1, child2 in zip(children1, children2):
        if not _xml_element_equal(child1, child2):
            return False
    return True

def xml_equal(str1, str2):
    et1 = ET.fromstring(str1)
    et2 = ET.fromstring(str2)
    return _xml_element_equal(et1, et2)


