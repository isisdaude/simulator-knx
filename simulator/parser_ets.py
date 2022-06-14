""" Parser of ETS project files """
from bs4 import BeautifulSoup
import os, sys, logging

"""
Devices types:

- Physical Sensors (Movement)
- Lightning Control
- Heating, A/C, Ventilation
- Presence detectors
- heating, air condition, ventilation
"""


class Manufacturer:
    def __init__(self, man_name, man_language):
        self.man_name = man_name
        self.man_language = man_language

    def __str__(self):
        return f" {self.man_name} -- Id: {self.man_refid} -- DefaultLanguage: {self.man_language}"

    def __repr__(self):
        return f" {self.man_name} -- Id: {self.man_refid}"


def build_manufacturers_list(master_parser, project_files_path):
    manufacturers = master_parser.find_all("Manufacturer")
    man_list = []
    for folder_name in os.listdir(project_files_path):
        if (
            os.path.isdir(project_files_path + folder_name) and folder_name[0:2] == "M-"
        ):  # check if the folder has the refid of a manufacturer
            man_refid = folder_name
            for manufacturer in manufacturers:
                if manufacturer["Id"] == man_refid:
                    man_name = manufacturer["Name"]
                    try:
                        man_language = manufacturer["DefaultLanguage"]
                    except KeyError:  # if no default language
                        man_language = ""
                        logging.info(
                            f" <ETS files parser> No Default Language for {man_name} ({man_refid})."
                        )
                        man_obj = Manufacturer(man_refid, man_name, man_language)
                    man_list.append(man_obj)
    return man_list


class Item:
    def __init__(
        self,
        manufacturer_refid,
        manufacturer_name,
        firstlevel_section_refid,
        firstlevel_section_name,
        secondlevel_section_refid,
        secondlevel_section_name,
        item_refid,
        item_name,
        item_product_refid,
        item_hardware2program_refid,
    ):

        self.manufacturer_refid = manufacturer_refid
        self.manufacturer_name = manufacturer_name
        self.firstlevel_section_refid = firstlevel_section_refid
        self.firstlevel_section_name = firstlevel_section_name
        self.secondlevel_section_refid = secondlevel_section_refid
        self.secondlevel_section_name = secondlevel_section_name
        self.item_product_refid = item_product_refid
        self.item_hardware2program_refid = item_hardware2program_refid
        self.item_refid = item_refid
        self.item_name = item_name

    def __str__(self):
        return f"\nItem: '{self.item_name}' -- Id: {self.item_refid} \n\
∟ CatalogSections: {self.firstlevel_section_name} => {self.secondlevel_section_name} \n\
∟ Manufacturer: {self.manufacturer_name} -- Id: {self.manufacturer_refid}"


def find_english_name(refid, languages_translation_units):
    for unit in languages_translation_units:
        for element in unit.findChildren("translationelement", recursive=False):
            if element["refid"] == refid:
                for translation in element.findChildren("translation", recursive=False):
                    if translation["attributename"] == "Name":
                        return translation["text"]  # name if the frst section
    return None  # if no translation found


def build_devices_list(project_files_path, manufacturers_list):
    """Parse Catalog.xml files to list all devices (called items) present in the project"""
    items = []
    for man in manufacturers_list:
        manufacturer_refid = (
            man.man_refid
        )  # frst letter upper case because 'xml' feature and not 'lxml' for manufacturers
        manufacturer_name = man.man_name
        file_path = project_files_path + manufacturer_refid + "/Catalog.xml"
        # Open and parse the Catalog section of file Catalog.xml (gathering all devices with their parent catalog sections)
        catalog_file = open(file_path, "r")
        catalog_content = catalog_file.read()
        catalog_parser = BeautifulSoup(
            catalog_content, "lxml"
        )  # 'lxml' for the catalog, don't ask me why
        # print(f"[INFO]Size of catalog_parser for {manufacturer_refid}: {sys.getsizeof(catalog_parser)} bytes")

        # Parse the Language section of the file to store all information in english, no matter the default language of the manufacturer, considering the user language is us_-English
        languages = catalog_parser.find(
            identifier="en-US"
        )  # with lower-case first letter, different from the actual file, maybe because of 'lxml' beutiful soup feature
        languages_translation_units = languages.find_all(
            "translationunit"
        )  # get all language translation for the devices of this manufacturer that are present in the project
        catalog = catalog_parser.find(
            "catalog"
        )  # begining pf catalog tree of devices from this maufacturer in the current project
        # loop on all 1st level of catalogsection (in case there is more than one subsection)
        for firstlevel_section in catalog.findChildren(
            "catalogsection", recursive=False
        ):
            firstlevel_section_refid = firstlevel_section["id"]
            name = find_english_name(
                firstlevel_section_refid, languages_translation_units
            )
            firstlevel_section_name = (
                name if name else firstlevel_section["name"]
            )  # if no translation found
            # loop on all sub catalogsection for the current 1st level catalog section
            for secondlevel_section in firstlevel_section.findChildren(
                "catalogsection", recursive=False
            ):
                secondlevel_section_refid = secondlevel_section["id"]
                name = find_english_name(
                    secondlevel_section_refid, languages_translation_units
                )
                secondlevel_section_name = (
                    name if name else secondlevel_section["name"]
                )  # if no translation found
                # loop on all item defined under this 2-level catalogsections
                for item in secondlevel_section.findChildren(
                    "catalogitem", recursive=False
                ):
                    item_refid = item["id"]
                    item_product_refid = item["productrefid"]
                    item_hardware2program_refid = item["hardware2programrefid"]
                    name = find_english_name(item_refid, languages_translation_units)
                    item_name = name if name else item["name"]
                    item_obj = Item(
                        manufacturer_refid,
                        manufacturer_name,
                        firstlevel_section_refid,
                        firstlevel_section_name,
                        secondlevel_section_refid,
                        secondlevel_section_name,
                        item_refid,
                        item_name,
                        item_product_refid,
                        item_hardware2program_refid,
                    )
                    items.append(item_obj)
    return items


def main():  # TODO: consider device number in the case of multiple instances of the same deviiec in a project
    # get and parse the master file to build list of manufacturers names, reference Id and languages
    project_files_path = "./docs/catalog/catalogproject_sensors/"
    master_file = open(project_files_path + "knx_master.xml", "r")
    master_content = master_file.read()
    master_parser = BeautifulSoup(master_content, "xml")  # 'xml' for knx_master
    # print(f"[INFO] Size of master_parser: {sys.getsizeof(master_parser)} bytes")
    manufacturers_list = build_manufacturers_list(master_parser, project_files_path)
    print("\n------ Manufacturers in this project ------ \n")
    for man in manufacturers_list:
        print(man)
    items_list = build_devices_list(project_files_path, manufacturers_list)
    print("\n------ Devices(Items) in this project ------ ")
    for item in items_list:
        print(item)
    logging.info(
        f"<ETS files parser> Size of manufacturers_list: {sys.getsizeof(manufacturers_list)} bytes."
    )
    logging.info(
        f"<ETS files parser> Size of items_list: {sys.getsizeof(items_list)} bytes.\n"
    )
    # (size of items list for 6 devices: 120B, for 60 devices: 664B, size of man_list:120B)


if __name__ == "__main__":
    main()
