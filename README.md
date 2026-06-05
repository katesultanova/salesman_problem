# salesman_problem
# Analiza Porównawcza Algorytmów dla Problemu Komiwojażera (TSP)

Projekt akademicki dedykowany implementacji, wizualizacji oraz analizie wydajnościowej trzech różnych podejść do klasycznego Problemu Komiwojażera (Traveling Salesperson Problem). Głównym celem programu jest wyznaczenie najkrótszego Cyklu Hamiltona w grafie pełnym ważonym na podstawie współrzędnych dwuwymiarowych.

## 🚀 Zaimplementowane Algorytmy

1. **MST-DFS (Metoda Aproksymacyjna):** Wielomianowa heurystyka dedykowana dla Metrycznego TSP. Buduje Minimalne Drzewo Rozpinające (algorytm Kruskala), wykonuje pełne przejście w głąb (DFS) z backtrackingiem, a następnie realizuje skracanie ścieżki (*shortcutting*) poprzez eliminację duplikatów za pomocą unikalnych kluczy słownika Pythona. Złożoność obliczeniowa wynosi $\mathcal{O}(n^2)$.
2. **Brute Force (Metoda Siłowa):** Algorytm dokładny generujący wszystkie możliwe permutacje tras za pomocą modułu `itertools.permutations`. Gwarantuje znalezienie optimum globalnego, jednak jego silniowa złożoneść czasowa $\mathcal{O}(n!)$ ogranicza jego stosowanie do małych instancji ($N \le 10$).
3. **Branch and Bound (Metoda Podziału i Ograniczeń):** Zaawansowany algorytm dokładny zrealizowany na podstawie koncepcji Little'a. Wykorzystuje cykliczną redukcję macierzy kosztów (odejmowanie minimów wierszami i kolumnami) do wyznaczania dynamicznych ograniczeń dolnych (*Bound*) oraz nakłada nieskończoności ($\infty$) w celu blokowania przedwczesnych podcykli. Umożliwia to wydajne odcinanie (*pruning*) nieefektywnych gałęzi drzewa stanów.

## 📦 Wymagania i Instalacja

Program został napisany w języku Python 3.
Do poprawnego działania i generowania wykresów wymagane jest zainstalowanie zewnętrznych bibliotek numerycznych oraz graficznych. 

Instalacja pakietów za pomocą menedżera `pip`:

```bash
pip install numpy scipy networkx matplotlib
```
## 🛠️ Topologie Grafów i Zestawy Testowe

W kodzie źródłowym przygotowano 5 skrajnie różnych zestawów danych, pozwalających zbadać wpływ geometrii wierzchołków na efektywność algorytmów:

* **Zestaw 1 (Domyślny):** Mały graf ($N=5$) stanowiący dokładne odzwierciedlenie matematycznego przykładu obliczeniowego z programu Maxima.
* **Zestaw 2:** Średni graf ($N=11$) reprezentujący losowo rozrzucone punkty.
* **Zestaw 3 (Gwiazda):** Jeden punkt centralny, pozostałe na okręgu ($N=10$). Wysoce symetryczny układ, będący trudnym testem dla mechanizmu odcięć algorytmu B&B.
* **Zestaw 4 (Rozbudowany):** Duża instancja ($N=16$) stanowiąca *crash test* dla algorytmów dokładnych. Pokazuje pełną kapitulację metody Brute Force ze względu na eksplozję kombinatoryczną.
* **Zestaw 5 (Klastry):** Dwie silnie odseparowane od siebie grupy miast ($N=10$). Układ idealny dla algorytmu Little'a, umożliwiający błyskawiczne odrzucanie niefektywnych gałęzi.

## 📊 Uruchomienie i Raportowanie

Aby przetestować inną topologię, wystarczy odkomentować odpowiednią linię w sekcji `DANE WEJŚCIOWE` kodu źródłowego i uruchomić skrypt:

## Wynik działania
Konsola: Generuje surową macierz odległości, ścieżkę multigrafu DFS, ostateczną listę wykonanych skrótów oraz tabelaryczne, precyzyjne zestawienie wydajnościowe.

Wizualizacja graficzna: Wyświetla okno matplotlib podzielone na sekcje: strukturę wyznaczonego drzewa MST z wagami krawędzi, finalną trasę wyznaczoną przez heurystykę MST-DFS, a także niezależne, profesjonalne wykresy dla optymalnych tras znalezionych przez Brute Force oraz Branch and Bound.
## Autor
Katsiaryna Sultanava
