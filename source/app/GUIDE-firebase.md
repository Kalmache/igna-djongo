# Brancher l'application Igna Djongo sur internet (Firebase)

Firebase est un service gratuit de Google. Il garde les membres, les paiements et l'histoire
en ligne, pour que tout le monde voie la même chose. Il faut le faire **une seule fois**,
de préférence sur un ordinateur (c'est plus facile que sur téléphone). Compte environ 10 minutes.

## 1. Créer le projet
1. Va sur https://console.firebase.google.com et connecte-toi avec ton compte Gmail.
2. Touche **Créer un projet**. Nom : `igna-djongo`. Accepte les conditions.
3. Quand on te propose **Google Analytics**, désactive-le (pas besoin). Touche **Créer le projet**.

## 2. Activer la connexion par numéro + code
1. Dans le menu de gauche : **Créer** (ou *Build*) puis **Authentication**, puis **Commencer**.
2. Choisis **Adresse e-mail/Mot de passe**, active le premier bouton, puis **Enregistrer**.
   (L'application transforme le numéro de téléphone et le code en identifiants : personne n'a besoin d'e-mail.)

## 3. Créer la base de données
1. Menu de gauche : **Créer** puis **Firestore Database**, puis **Créer une base de données**.
2. Emplacement : choisis **eur3 (Europe)** ou **europe-west**. Puis **Mode production**, puis **Créer**.
3. Ouvre l'onglet **Règles**. Efface tout ce qui est écrit, colle le contenu du fichier
   `firestore.rules` (je te l'envoie), puis touche **Publier**.

## 4. M'envoyer la « configuration »
1. En haut à gauche, touche la roue dentée puis **Paramètres du projet**.
2. En bas, dans « Vos applications », touche le symbole **</>** (Web).
3. Surnom : `igna-djongo`. Ne coche pas « Firebase Hosting ». Touche **Enregistrer l'application**.
4. Un bloc apparaît avec `const firebaseConfig = { apiKey: "...", authDomain: "...", ... }`.
   **Copie ce bloc et envoie-le moi ici.** Ce n'est pas un mot de passe : il est fait pour être dans l'application.

C'est tout. Je branche l'application, puis on passe à l'étape 3 (la mettre en ligne et le lien WhatsApp).

## Ensuite, dans l'application
- **Le premier compte créé devient responsable et trésorier.** Crée le tien en premier.
- À ce moment, le **code de l'igna** que tu tapes devient le code officiel (par exemple `djongo2026`).
  Tu le donnes sur le groupe WhatsApp : sans lui, personne ne peut créer de compte.
- Dans **Réglages > Qui fait quoi**, tu choisis qui est trésorier (seuls eux enregistrent les paiements)
  et qui est responsable.
