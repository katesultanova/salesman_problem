import numpy as np
import itertools
import networkx as nx
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import time

# 1. DANE WEJŚCIOWE (Współrzędne miast i generowanie macierzy wag)

# Zestaw 1: przykład z pliku maxima
points = np.array([[0,0],[1,7],[-2,4],[2,8],[0,11]])

# Zestaw 2: Średni graf 
#points = np.array([[10, 10], [25, 50], [40, 15], [50, 85], [80, 20], [90, 60], [35, 35], [70, 95], [15, 30], [65, 45], [55, 10]])

#Zestaw 3: Jeden punkt centralny, reszta na okręgu (Trudny test dla B&B)
#points = np.array([[50, 50],[10, 10], [10, 90], [90, 10], [90, 90],[50, 10], [50, 90], [10, 50], [90, 50], [25, 25]])

# Zestaw 4: rozbudowany: 16 miast (Crash test dla B&B, zablokuj Brute Force!)
#points = np.array([[10, 10], [20, 80], [35, 40], [90, 15], [80, 75], [45, 85], [15, 45], [65, 20],[50, 55], [30, 25], [70, 60], [85, 35],[25, 95], [60, 90], [95, 80], [40, 5]])

#Zestaw 5: Dwie odseparowane grupy miast
#points = np.array([[5, 5], [8, 12], [12, 6], [15, 15], [6, 18],[85, 85], [90, 75], [78, 82], [95, 90], [82, 95]])

n_nodes = len(points)

# Wyznaczenie macierzy odległości (Euklidesowej)
dist_matrix = distance_matrix(points, points)

print("=== KROK 0: MACIERZ ODLEGŁOŚCI (DANE WEJŚCIOWE) ===")
print("Indeksy miast: 0, 1, 2, 3, 4\n")
print(np.round(dist_matrix, 2))
print("-" * 60)

# Budowanie pełnego grafu wejściowego G w bibliotece NetworkX
G = nx.Graph()
G.add_nodes_from(range(n_nodes))
for i, j in itertools.combinations(range(n_nodes), 2):
    G.add_edge(i, j, weight=dist_matrix[i][j])


# =====================================================================
# 2. DEFINICJE FUNKCJI ALGORYTMÓW
# =====================================================================
def minimum_spanning_tree(G):
    """Wyznacza Minimalne Drzewo Rozpinające (MST) algorytmem Kruskala."""
    #inicjalizacja pustego grafu
    T = G.__class__()#tworzy pusty graf  na podstawie wejściowego
    T.add_nodes_from(G.nodes)#kopiuje wierzch 
    edges = list(G.edges(data=True))#pobiera listę wszystkich dostępnych połączen w grafie z ich wagami
    edges.sort(key=lambda x: x[2]['weight'])#sortowanie krawędz od najkr do najdłuższej

    
    for u, v, attrs in edges: #główna p. zachłanna
        if nx.has_path(T, u, v): # sprawdzamy czy są połączone dla unikania cykli 
            continue
        T.add_edge(u, v, **attrs)#dodanie krawedzi
    return T


def dfs_gen(G, v=0, parent=None):
    """Generator przeszukiwania w głąb (DFS) zapisujący pełną ścieżkę (z powrotami)."""
    if v == 0:
        yield v# alg zapisuje punkt startowy jako pierwsz el. trasy
    for u in G.adj[v]:#sprawdza sąsiadów
        if u != parent:
            yield u
            yield from dfs_gen(G, u, v) #przekazujemy wartości 
            yield v

def uniwersalny_brute_force(dist_matrix):
    """Wyszukiwanie optymalne metodą siłową (dwie pętle z itertools)."""
    n = len(dist_matrix)
    wzystkie_permutacje = itertools.permutations(range(1, n))
    
    minimalny_koszt = float('inf')
    najlepsza_trasa = None
    
    for perm in wzystkie_permutacje:
        aktualna_trasa = [0] + list(perm) + [0]
        aktualny_koszt = 0
        
        for i in range(n):
            miasto_startowe = aktualna_trasa[i]
            miasto_docelowe = aktualna_trasa[i + 1]
            aktualny_koszt += dist_matrix[miasto_startowe][miasto_docelowe]
            
        if aktualny_koszt < minimalny_koszt:
            minimalny_koszt = aktualny_koszt
            najlepsza_trasa = [0] + list(perm)
            
    return najlepsza_trasa, minimalny_koszt


##########################################################
def metoda_little_branch_and_bound(dist_matrix):
    """
    Implementacja metody Branch and Bound na podstawie redukcji macierzy kosztów.
    Zgodna z krokami 1-6 z materiałów wykładowych.
    """
    n = len(dist_matrix)
    
    # KROK 1: Kopiujemy macierz i ustawiamy przekątną na nieskończoność (blokada jazdy do samego siebie)
    macierz_startowa = np.copy(dist_matrix)
    for i in range(n):
        macierz_startowa[i][i] = np.inf
        
    # Słownik przechowujący najlepsze globalne wyniki (UB = ograniczenie górne)
    rekord = {
        'najlepszy_koszt': np.inf,
        'najlepsza_trasa': []
    }

    # POMOCNICZA FUNKCJA REDUKCJI 
    def redukuj_macierz(mat):
        r_suma = 0
        # Redukcja wierszy: odejmowanie minimum z każdego wiersza w celu utworzenia zera
        for i in range(n):
            min_wiersza = np.min(mat[i])
            if min_wiersza < np.inf and min_wiersza > 0:
                r_suma += min_wiersza
                mat[i] = mat[i] - min_wiersza
        # Redukcja kolumn: odejmowanie minimum z każdej kolumny w celu utworzenia zera
        for j in range(n):
            min_kolumny = np.min(mat[:, j])
            if min_kolumny < np.inf and min_kolumny > 0:
                r_suma += min_kolumny
                mat[:, j] = mat[:, j] - min_kolumny
        return r_suma  # Zwraca sumę kosztów odjętych stałych redukcji (R)

    # GLÓWNA REKURENCJA 
    def szukaj_w_drzewie(obecna_macierz, obecna_trasa, obecny_lb):
        poziom = len(obecna_trasa)
        i = obecna_trasa[-1] # Nasz przodek (miasto z którego ruszamy)

        # Warunek bazowy: odwiedziliśmy wszystkie miasta (Krok 4/5)
        if poziom == n:
            # Dodajemy koszt powrotu do bazy (miasta 0) z ostatniego miasta
            koszt_koncowy = obecny_lb + obecna_macierz[i][0]
            if koszt_koncowy < rekord['najlepszy_koszt']:
                rekord['najlepszy_koszt'] = koszt_koncowy
                rekord['najlepsza_trasa'] = obecna_trasa + [0]
            return

        # Przeglądamy potencjalnych potomków j (kolejne miasta do odwiedzenia)
        for j in range(n):
            if j not in obecna_trasa and obecna_macierz[i][j] < np.inf:
                
                # KROK 3: Kopiujemy macierz przodka dla nowego potomka j
                macierz_potomka = np.copy(obecna_macierz)
                koszt_przejscia_i_j = macierz_potomka[i][j]
                
                # Wpisujemy nieskończoność w wiersz przodka i kolumnę potomka (wykluczenie ich z dalszych ruchów)
                macierz_potomka[i, :] = np.inf
                macierz_potomka[:, j] = np.inf
                
                # Wpisujemy nieskończoność w komórkę powrotną (j, i) - BLOKADA PRZEDWCZESNEGO PODCYKLU
                macierz_potomka[j][i] = np.inf
                
                # Jeśli to jeszcze nie jest koniec podróży, blokujemy przedwczesny powrót do miasta startowego 0
                if poziom < n - 1:
                    macierz_potomka[j][0] = np.inf

                # KROK 4: Liczymy koszt redukcji nowej macierzy potomka po nałożeniu blokad inf
                r_j = redukuj_macierz(macierz_potomka)
                
                # Całkowity koszt dolny (LB) potomka j zgodnie ze wzorem z wykładu
                nowy_lb = obecny_lb + koszt_przejscia_i_j + r_j
                
                # KROK 6: Ograniczenie (PRUNING) - rozwijamy gałąź tylko, jeśli jej koszt LB rokuje lepiej niż obecny rekord UB
                if nowy_lb < rekord['najlepszy_koszt']:
                    szukaj_w_drzewie(macierz_potomka, obecna_trasa + [j], nowy_lb)

    # URUCHOMIENIE ALGORYTMU
    # Krok 2: Pierwsza redukcja macierzy dla punktu startowego (0) wyznaczająca początkowy Bound rzędu R
    pierwszy_lb = redukuj_macierz(macierz_startowa)
    
    # Krok 3: Startujemy przeszukiwanie drzewa od miasta 0
    szukaj_w_drzewie(macierz_startowa, [0], pierwszy_lb)
    
    # Zwracamy trasę (obcinamy końcowe zero, by pasowało do formatu Twojego kodu) i koszt
    return rekord['najlepsza_trasa'][:-1], rekord['najlepszy_koszt']



# =====================================================================
# 3. URUCHOMIENIE I DOKŁADNY POMIAR CZASU: MST-DFS
# =====================================================================
# START stopera przed budową drzewa MST
start_mst_dfs = time.perf_counter()

T_mst = minimum_spanning_tree(G)
full_dfs_path = list(dfs_gen(T_mst))

print("=== KROK 2: PEŁNE PRZEJŚCIE DFS DRZEWA MST (Z POWROTAMI) ===")
print(f"Pełna trajektoria (multigraf): {full_dfs_path}")
print("-" * 60)

hamilton_cycle = list(dict.fromkeys(full_dfs_path))

print("=== KROK 3: SKRACANIE ŚCIEŻKI I WYNIK KOŃCOWY (CYKL HAMILTONA) ===")
print(f"Wyznaczone skróty (usunięto powtórzenia wierzchołków): {hamilton_cycle}")

tsp_edges = []
final_tsp_cost = 0 
for i in range(len(hamilton_cycle)):
    u = hamilton_cycle[i]
    v = hamilton_cycle[0] if i == len(hamilton_cycle) - 1 else hamilton_cycle[i+1]
    
    edge_cost = dist_matrix[u][v]
    tsp_edges.append((u, v, edge_cost))
    final_tsp_cost += edge_cost

# KONIEC stopera dla metody MST-DFS
end_mst_dfs = time.perf_counter()
czas_mst_dfs = end_mst_dfs - start_mst_dfs

print("\nOstateczne krawędzie w cyklu TSP:")
for u, v, c in tsp_edges:
    print(f"   Połączenie {u} -> {v} (odległość: {c:.2f})")

print(f"\nCAŁKOWITY KOSZT TRASY (Suma cyklu Hamiltona): {final_tsp_cost:.2f}")
print("=" * 60)


# =====================================================================
# 4. URUCHOMIENIE I DOKŁADNY POMIAR CZASU: BRUTE FORCE
# =====================================================================
start_bf = time.perf_counter()

# Wywołujemy poprawną, nową funkcję uniwersalną
bf_trasa, bf_koszt = uniwersalny_brute_force(dist_matrix)
#bf_trasa=[0,1]
#bf_koszt=0
end_bf = time.perf_counter()
czas_bf = end_bf - start_bf

print("=== WYNIK BRUTE FORCE (WIDOK Z 2 PĘTLI) ===")
print(f"Najlepsza trasa: {bf_trasa}")
print(f"Koszt minimalny: {bf_koszt:.2f}")
print("-" * 60)

# Sparowanie wyników uniwersalnego Brute Force dla potrzeb dedykowanego wykresu
bf_edges = []
for i in range(len(bf_trasa)):
    u = bf_trasa[i]
    v = bf_trasa[0] if i == len(bf_trasa) - 1 else bf_trasa[i+1]
    bf_edges.append((u, v, dist_matrix[u][v]))


# --- METODA 3: BRANCH AND BOUND  ---
start_bb = time.perf_counter()
bb_trasa, bb_koszt = metoda_little_branch_and_bound(dist_matrix)
end_bb = time.perf_counter()
czas_bb = end_bb - start_bb

bb_edges = []
for i in range(len(bb_trasa)):
    u, v = bb_trasa[i], bb_trasa[(i + 1) % n_nodes]
    bb_edges.append((u, v, dist_matrix[u][v]))

# =====================================================================
# 4. ZAKTUALIZOWANE PODSUMOWANIE CZASOWE DLA 3 METOD 
# =====================================================================
print("\n" + "="*80)
print("   ZESTAWIENIE WYDAJNOŚCIOWE ALGORYTMÓW DLA N = 10 (DANE DO RAPORTU)")
print("="*80)
print(f"{'Kryterium Porównawcze':<25} | {'Metoda MST-DFS':<15} | {'Metoda Brute Force':<15} | {'Metoda Branch&Bound':<15}")
print("-"*80)
print(f"{'Wyznaczony koszt':<25} | {final_tsp_cost:<15.2f} | {bf_koszt:<15.2f} | {bb_koszt:<15.2f}")
print(f"{'Czas wykonania [s]':<25} | {czas_mst_dfs:<15.6f} | {czas_bf:<15.6f} | {czas_bb:<15.6f}")
print("="*80 + "\n")

# =====================================================================
# 6. WIZUALIZACJA 
# =====================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Wykres 1: Minimalne Drzewo Rozpinające (MST)
ax1.set_title("1. Wyznaczone Drzewo MST", fontsize=12, weight='bold')
for u, v, data in T_mst.edges(data=True):
    ax1.plot([points[u][0], points[v][0]], [points[u][1], points[v][1]], color='#585A9D', linewidth=3)
    ax1.text((points[u][0] + points[v][0]) / 2, (points[u][1] + points[v][1]) / 2, 
             f"{data['weight']:.1f}", fontsize=10, color='darkred', ha='center', va='center', weight='bold')

# Wykres 2: Finalna Trasa TSP (MST-DFS)
ax2.set_title(f"2. Finalna Trasa TSP (Koszt: {final_tsp_cost:.2f})", fontsize=12, weight='bold')
for u, v, cost in tsp_edges:
    ax2.plot([points[u][0], points[v][0]], [points[u][1], points[v][1]], color='red', linewidth=3)
    ax2.text((points[u][0] + points[v][0]) / 2, (points[u][1] + points[v][1]) / 2, 
             f"{cost:.1f}", fontsize=10, color='blue', ha='center', va='center', weight='bold')

# Wspólne formatowanie obu wykresów
for ax in (ax1, ax2):
    ax.scatter(points[:, 0], points[:, 1], color='#272541', s=500, zorder=3)
    for i, (x, y) in enumerate(points):
        ax.text(x, y, str(i), color='white', fontsize=11, ha='center', va='center', weight='bold', zorder=4)
    ax.axis('off') 

plt.tight_layout()
plt.show()


# =====================================================================
# WYKRES: OPTYMALNA TRASA BRUTE FORCE
# =====================================================================
fig, ax = plt.subplots(figsize=(7, 6))
ax.set_title(f"Optymalna Trasa Brute Force (Koszt: {bf_koszt:.2f})", fontsize=12, weight='bold')

# 1. Rysowanie zielonych krawędzi trasy optymalnej
for u, v, cost in bf_edges:
    ax.plot([points[u][0], points[v][0]], [points[u][1], points[v][1]], color='#2E7D32', linewidth=3, zorder=1)
    ax.text((points[u][0] + points[v][0]) / 2, (points[u][1] + points[v][1]) / 2, 
            f"{cost:.1f}", fontsize=10, color='purple', ha='center', va='center', weight='bold', zorder=2)

# 2. Rysowanie miast
ax.scatter(points[:, 0], points[:, 1], color='#272541', s=500, zorder=3)

# 3. Dodanie białych numerów miast wewnątrz kółek
for i, (x, y) in enumerate(points):
    ax.text(x, y, str(i), color='white', fontsize=11, ha='center', va='center', weight='bold', zorder=4)

ax.axis('off') 
plt.tight_layout()
plt.show()

# =====================================================================
# 6. WYKRES: TRASA BRANCH AND BOUND
# =====================================================================
fig, ax = plt.subplots(figsize=(7, 6))
ax.set_title(f"Optymalna Trasa Branch and Bound (Koszt: {bb_koszt:.2f})", fontsize=12, weight='bold')

for u, v, cost in bb_edges:
    ax.plot([points[u][0], points[v][0]], [points[u][1], points[v][1]], color='#2E7D32', linewidth=3, zorder=1)
    ax.text((points[u][0] + points[v][0]) / 2, (points[u][1] + points[v][1]) / 2, 
            f"{cost:.1f}", fontsize=9, color='purple', ha='center', va='center', weight='bold', zorder=2)

ax.scatter(points[:, 0], points[:, 1], color='#272541', s=400, zorder=3)
for i, (x, y) in enumerate(points):
    ax.text(x, y, str(i), color='white', fontsize=10, ha='center', va='center', weight='bold', zorder=4)

ax.axis('off') 
plt.tight_layout()
plt.show()