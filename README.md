# Laboratorium Technologii Sieciowych
Politechnika Śląska - 2026
## Wprowadzenie do platformy Azure - Instrukcja


### Wymagania
Niezbędne:
- Konto na platformie MS Azure
- Konto GitHub

Opcjonalne:
- Python
- Lokalnie uruchomiony serwer MySQL

### Cel
Celem tego ćwiczenia jest zdeployowanie prostej aplikacji do zarządzania budżetem domowym w Azure.

### Zalogowanie się do portalu
Azure Portal:
https://portal.azure.com/#home

Logujemy się adresem uczelnianym.

### Utworzenie grupy zasobów
1. Przechodzimy w widok Resource Groups
2. Klikamy *Create*
3. Uzupełniamy dane
    1. Nazwa RG:</br>my-first-azure-app-rg-{nr_indeksu}
    2. Region:</br>Poland Central
    3. Subskrypcja:</br>Azure for Students
4. Klikamy *Review + Create*
5. Klikamy *Create*

### Provisioning App Service
W pasku wyszukiwania u góry wpisujemy hasło `web app`. Wybieramy usługę *Web App* z podsekcji Marketplace.
<img width="2056" height="682" alt="Pasted image 20260109103907" src="https://github.com/user-attachments/assets/e6fa8e7e-d981-4be0-b47d-b59ebde6e3c5" />


Wypełniamy formularz:
- *Resource Group*
  </br>Wybieramy utworzoną przez nas grupę zasobów
- *Name*
  </br>Proponuję: `my-first-azure-app-{nr_indeksu}`
- *Publish*
  </br>Zostawiamy opcję Code
- *Runtime Stack*
  </br>Python 3.14
- *Region*
  </br>Poland (Central)

Na ten moment to wystarczy. Przechodzimy do zakładki *Review and Create* i klikamy *Create*.
Provisioning usługi może chwile potrwać (około 5-10 minut).
### Fork Repozytorium
Tworzymy fork repozytorium
https://github.com/dkacza/lab-ts-azure

> Kopiujemy wszystkie branche, nie tylko main

### Pierwszy deployment i proste CI/CD
Główny branch zawiera prostą aplikację we Flasku, która wyświetli powitalny komunikat na ekranie przeglądarki. Stanowi to dobrą podstawę pod pierwszy deployment.

Lokalne uruchomienie aplikacji *dla chętnych*:
```sh
python -m venv venv 
source venv/bin/activate # Windows: venv\Scripts\activate 
pip install -r requirements.txt 
python app.py
```


1. Przechodzimy do naszej grupy zasobów i wybieramy nowo utworzoną usługę App Service.
2. Wybieramy opcję *Deployment > Deployment Center* po lewej stronie.
3. Uzupełniamy formularz:
    1. Source
       `CI/CD Github`
    2. *Logujemy się do naszego konta GitHub i udzielamy niezbędnych autoryzacji*
    3. Repository
       Utworzony Fork
    4. Branch
       `main`
4. Reszta ustawień pozostaje domyślna.
5. Klikamy *Save* u góry formularza.

Po chwili w naszym repozytorium na branchu `main` zobaczymy dodatkowe pliki związane z pipelinem CI/CD. Od teraz, każdy commit na główny branch będzie rozpoczynał deployment.

Automatycznie rozpocznie się również pierwszy deployment. Jego status można śledzić po kliknięciu na żółtą kropkę koło nazwy commita w GitHubie lub bezpośrednio w Azure.
<img width="964" height="309" alt="Pasted image 20260109105503" src="https://github.com/user-attachments/assets/8439d876-f0fa-433b-ad95-e20d3fbeaa5d" />
<img width="2056" height="659" alt="Pasted image 20260109105600" src="https://github.com/user-attachments/assets/025bf616-f528-479b-a362-5d8d1d9bd00d" />

W razie błędu deploymentu, należy uruchomić go ponownie z poziomu GitHuba.

Z poziomu App Service wchodzimy w link pod *Default Domain*. Uruchomienie aplikacji może chwile potrwać, zwłaszcza za pierwszym razem.

Finalnym rezultatem tego kroku powinno być:
<img width="2056" height="185" alt="Pasted image 20260109110520" src="https://github.com/user-attachments/assets/001eb131-f1ba-4716-b3fe-99d3cd024a18" />

### Obsługa bazy danych
Kolejnym celem jest budowa właściwej funkcjonalności aplikacji. Na branchu `db` zamieszczony został kod aplikacji dla tego podpunktu. Tworzy on połączenie z bazą danych na podstawie zadanych zmiennych środowiskowych.

Lokalne uruchomienie aplikacji *dla chętnych*:
```sh
cp .env.template .env
pip install -r requirements.txt

# Uruchomienie serwera MySQL - docker
docker run --name mysql -e MYSQL_ROOT_PASSWORD=Zaq12wsx -p 3306:3306 -d mysql:latest
docker exec -it mysql bash

# Wewnątrz kontera
mysql -u root -p # Podajemy hasło kiedy zostaniemy poproszeni
CREATE DATABASE budget_db CHARACTER SET utf8mb4;
exit # Wychodzimy z MySQL
exit # Wychodzimy z kontera

# Uruchomienie aplikacji
python app.py
```

#### Provisioning serwera MySQL
W pasku wyszukiwania wpisujemy `mysql` i wybieramy opcję *Azure Database for MySQL servers*.
<img width="2056" height="418" alt="Pasted image 20260109114113" src="https://github.com/user-attachments/assets/76e05bca-94aa-4f1c-992b-d9230cf5793e" />

Następnie klikamy *Create* i *Quick Create* we Flexible Server.

Uzupełniamy formularz:
1. *Resource Group*
   </br>Utworzona przez nas RG.
2. *Server Name*
   </br>Rekomenduję `my-first-azure-app-db-server-{nr_albumu}`
3. *Region*
   </br>Poland (Central)
4. *Admin login*
   </br>Możesz użyć dowolnej nazwy, aczkolwiek takie jak np. admin mogą sprawić problem przy deploymencie
5. *Password*
   </br>Użyj dowolnego hasła spełniającego warunki.
   > Upewnij się, że hasło nie zawiera znaków specjalnych zastrzeżonych przez MySQL (np. @)
6. *Workload Details*
   </br>Dev/Test

> WAŻNE
> Zapisz gdzieś użytkownika oraz hasło. Będą potrzebne później.

Resztę ustawień zostawić domyślną. Klikamy *Review + Create* i *Create*. Deployment może chwilę potrwać.

Po zakończeniu deploymentu przechodzimy do nowo utworzonego zasobu.
<img width="2056" height="719" alt="Pasted image 20260109120104" src="https://github.com/user-attachments/assets/a1f95716-ea41-4c12-806a-21af03d030e5" />

#### Utworzenie bazy danych
W widoku serwera bazy danych, klikamy *Connect*. Zapytani o włączenie publicznego dostępu z usług Azure do tego serwera klikamy *Yes*.

Wkrótce uruchomi się shell. Wpisujemy zapisane przez nas hasło.
<img width="2056" height="371" alt="Pasted image 20260109120439" src="https://github.com/user-attachments/assets/b5a82eb1-2c12-4d18-997e-61f693582aac" />

Tworzymy bazę danych korzystając z następującego polecenia w SQL
```sql
CREATE DATABASE budget_db CHARACTER SET utf8mb4;
```

Po utworzeniu bazy zamykamy sesję MySQL poleceniem `exit` i zamykamy Cloud Shell.

Zapisz również endpoint dostępu do serwera bazy danych.
#### Dodanie zmiennych środowiskowych w aplikacji
Baza danych jest gotowa do działania. Możemy połączyć z nią naszą aplikację. W tym celu należy dodać **zmienne środowiskowe**.

Wchodzimy w zdeployowaną usługę *App Service* i z zakładki *Settings* wybieramy sekcję *Environmental variables*.
<img width="2056" height="720" alt="Pasted image 20260109121036" src="https://github.com/user-attachments/assets/3e18dc52-633e-4a16-b61c-45223bfe75fd" />

Dodajemy niezbędne zmienne środowiskowe
```env
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_HOST=
MYSQL_DB=budget_db
MYSQL_PORT=3306
```

Pola `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST` należy uzupełnić zapisanymi wcześniej wartościami.

Po dodaniu wszystkich zmiennych klikamy *Apply.*
#### Deployment
Otwieramy PR. Mergujemy branch `db` do brancha `main`. Dzięki dołączonemu pipeline'owi CI/CD automatycznie uruchomi to deployment.

Po jego ukończeniu powinniśmy mieć działającą aplikację:
<img width="2056" height="470" alt="Pasted image 20260109122824" src="https://github.com/user-attachments/assets/8d1c6a57-5d16-46f9-801a-76ea79147235" />


### Usunięcie zaalokowanych zasobów
W celu uniknięcia naliczania kosztów, po zakończonym laboratorium, usuwamy całą grupę zasobów.
<img width="2056" height="854" alt="Pasted image 20260109135220" src="https://github.com/user-attachments/assets/6f53059c-3e42-461c-9034-824a1652e92f" />
