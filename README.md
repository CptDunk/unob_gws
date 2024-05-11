# unob_gws

repository for school web scraping project of unob IS

## Task

### 2. Naplnění dat o skupinách

Využijte zdroje dat pro získání informací o skupinách (GQL_UG) včetně struktury skupin. Vytvořte JSON datovou strukturu (kompatibilní se systemdata.json). Vytvořte program, který importuje data do GQL endpointů (s využitím mutací). Zabezpečte existenci propojení (ExternalIDs) se zdrojovým IS.<br />


### Společné podmínky

Testujte **duplicitu** dat, jednak přes externalid a jednak, kde je to možné, přes jména či jiné identifikátory.<br />

Pro práci s html daty (získání html stránek) použijte knihovnu **selenium** (headless mode).<br />

Vytvořte a publikujte **pypi package**. Součastí github respository (source for package) je i ipynb notebook s demonstrací využití (import package, run main code). Nechť je možné importovat funkci gather z root balíčku (pypi package).<br />

Hlavní funkce **gather()** pracuje s následujícími parametry:
    
    - username: Přihlašovací jméno

    - password: Přihlašovací heslo
    
    - config: {paths: {planovaneudalosti: “”, planovanivyuky_attributy: “”, vav_departments: “”. … }} (defaultni hodnota)
    
    - output (systemdata.json, writetogql)
    
    - **extras (token!)

U entit naplňte všechny atributy, pokud ve zdroji některé atributy nejsou, domluvte se na jejich dummy values.<br />

Pokud máte u entit k dispozici atributy navíc, navrhněte rozšíření GQL endpointu.<br />


# Progress so far:

### 17/04/2024 <br />

- "Bypassing" pop up auth + normal auth; Basic/Simple-Dimple seb scrape of certain tag "pre" <br />

- Find main key value in .json <br />

- Begining of group parsing <br />

### 11/05/2024 <br />

- Parse groups: <br />

    - Filter lists - nyní načte každou dvojici samostatně <br />

    - Filter duplicities (based on IDs) - Smaže neoriginální dvojičky <br />

# TODO

- Zdroj dat 2. a 3.?<br />

- externalIDs<br />

- GroupTypes - Které jsou nadřazené a jaké to jsou<br />

- Které dvojice jmen skupin s ID jsou správné (kde najdeme external IDs)<br />

- Finalizace datové struktury<br />

- Nahrání dat přes GQL endpoint<br />