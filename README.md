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
    
    - username: Přihlašovací jméno<br />

    - password: Přihlašovací heslo<br />
    
    - config: {paths: {planovaneudalosti: “”, planovanivyuky_attributy: “”, vav_departments: “”. … }} (defaultni hodnota)<br />
    
    - output (systemdata.json, writetogql)<br />
    
    - **extras (token!)<br />

U entit naplňte všechny atributy, pokud ve zdroji některé atributy nejsou, domluvte se na jejich dummy values.<br />

Pokud máte u entit k dispozici atributy navíc, navrhněte rozšíření GQL endpointu.<br />


# Progress so far:

### 17/04/2024 <br />

- "Bypassing" pop up auth + normal auth; Basic/Simple-Dimple seb scrape of certain tag "pre" <br />

- Find main key value in .json <br />

- Begining of group parsing <br />

# TODO

- externalIDs type<br />

- Parse groups:<br />
    
    - Filter lists<br />

    - Filter duplicities (based on IDs)<br />