# ZPRP - Design Proposal

Autorzy: Rafał Celiński, Mateusz Łukasiewicz, Przemysław Walecki

## Opis

Projekt ma na celu stworzenie aplikacji działającej z poziomu wiersza poleceń, której celem będzie swobodne konwertowanie plików typu Markdown na Typst i LaTeX. W ramach zadania stworzone zostanie AST (Abstract Syntax Tree), które pozwoli na odwzorowanie struktury dokumentów oraz ich konwersję.



## Harmonogram

| Data       | Zadania                                          |
| ---------- |--------------------------------------------------|
| 24.03.2025 | Repozytorium GitHub                              |
|            | Konfiguracja środowiska                          |
| 31.03.2025 | Zapoznanie z działaniem pandoc                   |
|            | Zapoznanie z dokumentacją markdown, typst, latex |
| 07.04.2025 | Projekt drzewa AST                               |
|            | Definicja interfejsu dla konwerterów             |
|            | Implementacja modułu do analizy składni Markdown |
|            |                                                  |
| 21.04.2025 | Mapowanie Markdown na AST                        |
|            | Implementacja modułu do analizy składni Typst    |
| 28.04.2025 | Mapowanie AST na Typst                           |
|            | Testy konwersji Markdown → Typst                 |
| 05.05.2025 | Implementacja modułu do analizy składni Latex    |
|            | Mapowanie AST na Latex                           |
| 12.05.2025 | Testy konwersji Markdown → Latex                 |
|            | Uzupełnianie zaległości                          |
| 19.05.2025 | Projektowanie i implementacja CLI                |
|            | Projektowanie i implementacja aplikacji webowej  |
|            |                                                  |
| 26.05.2025 | Przygotowanie paczki aplikacji                   |
|            | Uzupełnienie dokumentacji                        |
|            | Przygotowanie projektu do oddania                |

## Bibliografia

- <https://docs.python.org/3/>
- <https://typer.tiangolo.com/>
- <https://docs.github.com/en/actions>
- <https://pylint.readthedocs.io/en/stable/>
- <https://python-poetry.org/docs/>
- <https://www.mkdocs.org/getting-starte/>
- <https://www.latex-project.org/help/documentation/>
- <https://pandoc.org/>
- <https://typst.app/docs/>
- <https://www.markdownguide.org/>
- <https://github.com/casey/just>

## Planowana funkcjonalność

### Wymagania funkcjonalne

- Konwersja z Markdown w stylu Github na Typst
- Konwersja z Markdown w stylu Github na LaTeX
- Uniwersalne drzewo AST
- CLI

### Wymagania niefunkcjonalne

- Możliwość łatwego rozbudowania o nowe formaty plików - cała aplikacja będzie opierać się na strukturze AST. Nowe formaty będą musiały jedynie zaimplementować przetwarzanie tego drzewa bez konieczności znania składni Markdowna.

## Stos technologiczny

- Python
- Typer

## Narzędzia

- GitHub z Github Actions
- Pylint
- Black formatter
- MkDocs
- Tox
- Just

## Testy

1. Testy jednostkowe - sprawdzimy poszczególne komponenty aplikacji takie jak: parser Markdown, transformator AST, funkcje pomocnicze
2. Testy integracyjne - sprawdzany będzie cały przepływ przetwarzania dokumentu (porównywanie wynikowych plików ze wzorcami)
3. Testy CLI - sprawdzimy działanie aplikacji z perspektywy użytkownika końcowego
