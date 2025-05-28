
= Tabele
\ 
== Podstawowa tabela
\ 
#table(
	columns: 3,
	table.header([Nagłówek 1], [Nagłówek 2], [Nagłówek 3], ),
	[Komórka 1], [Komórka 2], [Komórka 3], 
	[Komórka 4], [Komórka 5], [Komórka 6], 
)
\ 
== Tabela z wyrównaniem
\ 
#table(
	columns: 3,
	table.header([Lewo], [Środek], [Prawo], ),
	[L1], [Ś1], [P1], 
	[L2], [Ś2], [P2], 
	[L3], [Ś3], [P3], 
)
\ 
== Tabela z formatowaniem
\ 
#table(
	columns: 3,
	table.header([Nazwa], [Opis], [Status], ),
	[*Projekt A*], [_Ważny projekt_], [Gotowy], 
	[*Projekt B*], [#strike[Anulowany]], [Anulowany], 
	[*Projekt C*], [```text W trakcie```], [W trakcie], 
)
\ 
== Tabela z linkami
\ 
#table(
	columns: 3,
	table.header([Strona], [URL], [Opis], ),
	[Google], [#link("https://google.com")[google.com]], [Wyszukiwarka], 
	[GitHub], [#link("https://github.com")[github.com]], [Hosting kodu], 
	[Stack Overflow], [#link("https://stackoverflow.com")[stackoverflow.com]], [Q&A dla programistów], 
)

