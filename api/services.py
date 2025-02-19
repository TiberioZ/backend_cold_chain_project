import requests
import pandas as pd
import os
import json
from datetime import datetime

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }


class ColdChainService:

    def __init__(self):
        pass

    async def post_temperature(self, temperature: float, timestamp: str, captorId: str):
        # Fonction helper pour obtenir le prochain ID de coupure
        def get_next_coupure_id():
            if os.path.exists('log_coupure.csv') and os.path.getsize('log_coupure.csv') > 0:
                coupures_df = pd.read_csv('log_coupure.csv')
                if len(coupures_df) > 0:
                    return max([int(id.split('_')[1]) for id in coupures_df['coupureID']]) + 1
            return 1


        # Gestion du fichier de température
        if os.path.exists('log_temperature.csv') and os.path.getsize('log_temperature.csv') > 0:
            existing_df = pd.read_csv('log_temperature.csv')
            
            # Vérifier si la ligne existe déjà
            duplicate = existing_df[
                (existing_df['capteurID'] == captorId) & 
                (existing_df['temperature'] == temperature) & 
                (existing_df['timestamp'] == timestamp)
            ].empty == False
            
            if not duplicate:
                new_row = pd.DataFrame({
                    'capteurID': [captorId],
                    'temperature': [temperature],
                    'timestamp': [timestamp]
                })
                existing_df = pd.concat([existing_df, new_row], ignore_index=True)
                existing_df.to_csv('log_temperature.csv', index=False)
        else:
            new_df = pd.DataFrame({
                'capteurID': [captorId],
                'temperature': [temperature],
                'timestamp': [timestamp]
            })
            new_df.to_csv('log_temperature.csv', index=False)

        # Gestion des coupures
        # Créer le fichier s'il n'existe pas
        if not os.path.exists('log_coupure.csv'):
            pd.DataFrame(columns=[
                'coupureID', 'capteurID', 'timestamp_debut', 'timestamp_fin',
                'temperature_coupure_4', 'temperature_coupure_3', 'temperature_coupure_2'
            ]).to_csv('log_coupure.csv', index=False)

        coupures_df = pd.read_csv('log_coupure.csv')

        # Vérifier les coupures en cours pour ce capteur pour chaque niveau
        coupures_4 = coupures_df[
            (coupures_df['capteurID'] == captorId) & 
            (coupures_df['temperature_coupure_4'] == 1) &
            (coupures_df['timestamp_fin'].isna())
        ]
        
        coupures_3 = coupures_df[
            (coupures_df['capteurID'] == captorId) & 
            (coupures_df['temperature_coupure_3'] == 1) &
            (coupures_df['timestamp_fin'].isna())
        ]
        
        coupures_2 = coupures_df[
            (coupures_df['capteurID'] == captorId) & 
            (coupures_df['temperature_coupure_2'] == 1) &
            (coupures_df['timestamp_fin'].isna())
        ]

        # Fermer les coupures si la température est redevenue normale
        if temperature <= 4.0 and len(coupures_4) > 0:
            coupures_df.loc[coupures_4.index, 'timestamp_fin'] = timestamp
        
        if temperature <= 3.0 and len(coupures_3) > 0:
            coupures_df.loc[coupures_3.index, 'timestamp_fin'] = timestamp
        
        if temperature <= 2.0 and len(coupures_2) > 0:
            coupures_df.loc[coupures_2.index, 'timestamp_fin'] = timestamp

        # Créer de nouvelles coupures pour chaque seuil dépassé
        if temperature > 4.0 and len(coupures_4) == 0:
            new_coupure = pd.DataFrame({
                'coupureID': [f'COUP_{get_next_coupure_id()}'],
                'capteurID': [captorId],
                'timestamp_debut': [timestamp],
                'timestamp_fin': [None],
                'temperature_coupure_4': [1],
                'temperature_coupure_3': [0],
                'temperature_coupure_2': [0]
            })
            coupures_df = pd.concat([coupures_df, new_coupure], ignore_index=True)

        if temperature > 3.0 and len(coupures_3) == 0:
            new_coupure = pd.DataFrame({
                'coupureID': [f'COUP_{get_next_coupure_id()}'],
                'capteurID': [captorId],
                'timestamp_debut': [timestamp],
                'timestamp_fin': [None],
                'temperature_coupure_4': [0],
                'temperature_coupure_3': [1],
                'temperature_coupure_2': [0]
            })
            coupures_df = pd.concat([coupures_df, new_coupure], ignore_index=True)

        if temperature > 2.0 and len(coupures_2) == 0:
            new_coupure = pd.DataFrame({
                'coupureID': [f'COUP_{get_next_coupure_id()}'],
                'capteurID': [captorId],
                'timestamp_debut': [timestamp],
                'timestamp_fin': [None],
                'temperature_coupure_4': [0],
                'temperature_coupure_3': [0],
                'temperature_coupure_2': [1]
            })
            coupures_df = pd.concat([coupures_df, new_coupure], ignore_index=True)

        # Sauvegarder les modifications
        coupures_df.to_csv('log_coupure.csv', index=False)

        return {"message": "Données traitées avec succès"}

    async def get_advise_for_food_item(self, barcode: str, capteurID: str):
        import pandas as pd
        import os

        # Vérifier si le capteur a déjà eu une coupure
        if os.path.exists('log_coupure.csv') and os.path.getsize('log_coupure.csv') > 0:
            coupures_df = pd.read_csv('log_coupure.csv')
            # Chercher si le capteur existe dans n'importe quelle ligne
            has_coupure_history = 1 if len(coupures_df[coupures_df['capteurID'] == capteurID]) > 0 else 0
        else:
            has_coupure_history = 0

        # Lecture de la table de correspondance
        table = pd.read_excel("./from_to_pnns_temperatures.xlsx")

        # Get food data from API
        food_data = self.get_food_data(barcode)
        
        # Extract category from the food data and get the first category if multiple exist
        category = food_data["Catégorie"].split(',')[0].strip()

        print(category)

        # Filter the table for matching category and get temperature
        matching_rows = table[table["categories"] == category]
        
        # Check if we found any matching categories
        if matching_rows.empty:
            return {
                "error": "No matching category found"
            }
            
        # Convert numpy.int64 to Python int
        temperature = float(matching_rows["temperature_limite"].iloc[0])

        # Vérifier les coupures actives pour le niveau de température approprié
        if temperature == 4:
            # Filtrer les coupures pour ce capteur et cette température
            relevant_coupures = coupures_df[
                (coupures_df['capteurID'] == capteurID) & 
                (coupures_df['temperature_coupure_4'] == 1) &
                (coupures_df['timestamp_fin'].notna())  # Seulement les coupures terminées
            ]
            
            # Vérifier la durée de chaque coupure
            has_long_coupure = False
            for _, coupure in relevant_coupures.iterrows():
                debut = datetime.strptime(coupure['timestamp_debut'], "%Y-%m-%d %H:%M:%S")
                fin = datetime.strptime(coupure['timestamp_fin'], "%Y-%m-%d %H:%M:%S")
                duree = (fin - debut).total_seconds() / 60  # Durée en minutes
                if duree >= 30:
                    has_long_coupure = True
                    break
            
            has_coupure_history = 1 if has_long_coupure else 0

        elif temperature == 3:
            relevant_coupures = coupures_df[
                (coupures_df['capteurID'] == capteurID) & 
                (coupures_df['temperature_coupure_3'] == 1) &
                (coupures_df['timestamp_fin'].notna())
            ]
            
            has_long_coupure = False
            for _, coupure in relevant_coupures.iterrows():
                debut = datetime.strptime(coupure['timestamp_debut'], "%Y-%m-%d %H:%M:%S")
                fin = datetime.strptime(coupure['timestamp_fin'], "%Y-%m-%d %H:%M:%S")
                duree = (fin - debut).total_seconds() / 60
                if duree >= 30:
                    has_long_coupure = True
                    break
            
            has_coupure_history = 1 if has_long_coupure else 0

        elif temperature == 2:
            relevant_coupures = coupures_df[
                (coupures_df['capteurID'] == capteurID) & 
                (coupures_df['temperature_coupure_2'] == 1) &
                (coupures_df['timestamp_fin'].notna())
            ]
            
            has_long_coupure = False
            for _, coupure in relevant_coupures.iterrows():
                debut = datetime.strptime(coupure['timestamp_debut'], "%Y-%m-%d %H:%M:%S")
                fin = datetime.strptime(coupure['timestamp_fin'], "%Y-%m-%d %H:%M:%S")
                duree = (fin - debut).total_seconds() / 60
                if duree >= 30:
                    has_long_coupure = True
                    break
            
            has_coupure_history = 1 if has_long_coupure else 0

        else:
            has_coupure_history = 0

        return {
            "temperature": temperature,
            "has_coupure_history": has_coupure_history
        }

    @staticmethod  # Add staticmethod decorator since this doesn't use self
    def get_food_data(barcode: str):  # Add barcode parameter
        """Récupère les informations d'un aliment à partir de son code-barres via l'API Open Food Facts."""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == 1:  # Produit trouvé
                    product = data.get("product", {})
                    return {
                        "Nom": product.get("product_name", "Non disponible"),
                        #"Marque": product.get("brands", "Non disponible"),
                        "Catégorie": product.get("pnns_groups_1", "Non disponible")
                        #"Ingrédients": product.get("ingredients_text", "Non disponible"),
                        #"Énergie (kcal)": product.get("nutriments", {}).get("energy-kcal_100g", "Non disponible"),
                        #"Conservation": product.get("conservation_conditions", "Non disponible"),
                        #"URL": product.get("url", "Non disponible")
                    }
                else:
                    return {"Erreur": "Produit non trouvé"}
            except requests.exceptions.JSONDecodeError:
                return {"Erreur": "Réponse JSON invalide"}
        else:
            return {"Erreur": f"Échec de la requête (statut {response.status_code})"}