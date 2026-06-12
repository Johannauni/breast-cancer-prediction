import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pickle

csv_path_train = "/Users/johannaroehr/Documents/Studium /4. Semester/Info/Prüfungsprojekt/breast-cancer_train.csv"
csv_path_test = "/Users/johannaroehr/Documents/Studium /4. Semester/Info/Prüfungsprojekt/breast-cancer_test.csv"

top_features = ['concave points_worst','concave points_mean','perimeter_worst','radius_worst','perimeter_mean','radius_mean','area_worst']

def load_data(path):
    return pd.read_csv(path)

def basic_info(df_train):
    print(df_train.shape)
    print(df_train.info())
    print(df_train.describe())

def class_distribution(df_train):
    malignant = (df_train["diagnosis"] == -1).sum()
    benign = (df_train["diagnosis"] == +1).sum()
    print(f"bösartig: {malignant}, gutartig: {benign}")

    plt.bar(["Gutartig", "Bösartig"], [benign, malignant])
    plt.title("Klassenverteilung")
    plt.show()

def compute_feature_statistics(df_train):
    # min. / max. / average radius
    min_radius = df_train.iloc[:, 1].min()
    max_radius = df_train.iloc[:, 1].max()
    av_radius = df_train.iloc[:, 1].mean()
    print(f"Radiusminimum: {min_radius}")
    print(f"Radiusmaximum: {max_radius}")
    print(f"Radiusmittelwert: {av_radius}")

    # min / max / average texture
    min_texture = df_train.iloc[:, 2].min()
    max_texture = df_train.iloc[:, 2].max()
    av_texture = df_train.iloc[:, 2].mean()
    print(min_texture)
    print(max_texture)
    print(av_texture)

def compute_scatterplots(df_train):
    #zusammenhang radius worst vs perimeter_mean
    colors = df_train["diagnosis"].map({+1: "black", -1: "red"})
    plt.scatter(df_train["radius_worst"], df_train["perimeter_mean"], c=colors)
    plt.title("radius worst vs perimeter_mean")
    plt.show()

    #perimeter worst vs concave points worst
    colors = df_train["diagnosis"].map({+1: "black", -1: "red"})
    plt.scatter(df_train["perimeter_worst"], df_train["concave points_worst"], c=colors)
    plt.title("perimeter worst vs concave points_worst")
    plt.show()

    #radius worst vs concavity mean
    colors = df_train["diagnosis"].map({+1: "black", -1: "red"})
    plt.scatter(df_train["radius_worst"], df_train["concavity_mean"], c=colors)
    plt.title("radius worst vs concavity mean")
    plt.show()

    #concavity_mean vs. fractal_dimension_mean
    colors = df_train["diagnosis"].map({+1: "black", -1: "red"})
    plt.scatter(df_train["concavity_mean"], df_train["fractal_dimension_mean"], c=colors)
    plt.title("concavity_mean vs. fractal_dimension_mean")
    plt.show()

def compute_correlation(df_train):
    corr = df_train.corr(numeric_only=True)
    print(f"Korrelation: \n{corr['diagnosis'].sort_values()}")

def boxplot_visualization(df_train):
    important_features = ["concave points_worst", "concavity_mean", "radius_worst", "perimeter_worst", "area_worst", "radius_mean"]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()

    for i, feature in enumerate(important_features):
        malignant = df_train[df_train["diagnosis"] == -1][feature]
        benign = df_train[df_train["diagnosis"] == +1][feature]

        axes[i].boxplot([benign, malignant], tick_labels=["Gutartig", "Bösartig"])
        axes[i].set_title(feature)
        axes[i].set_ylabel("Wert")

    plt.tight_layout()
    plt.show()

def create_validation_df(df_train):
    df_shuffled = df_train.sample(frac=1, random_state=42).reset_index(drop=True) #sample(frac=1) mischt den gesamten Datensatz; random_state=42 macht das Mischen reproduzierbar; reset_index(drop=True) setzt den Index nach dem Mischen zurück
    split = int(len(df_shuffled) * 0.7) #split berechnet den Schnitt bei 70%
    df_train = df_shuffled[:split]
    df_valid = df_shuffled[split:]
    return df_train, df_valid

def standardisation(df_train, features):
    X = df_train[features].values  # restliche Spalten (Features)
    mean_train = X.mean(axis=0)
    std_train = X.std(axis=0)
    X = (X - mean_train) / std_train  # Werte kalibireren
    return X, mean_train, std_train

def gradient_descent (df_train, lr, iterations,X):
    X_train = np.c_[np.ones(len(X)), X] # bias w[0] einfügen
    y_train = df_train['diagnosis'].values  # Klassifizierung
    # w reproduzierbar inititalisieren
    rng = np.random.default_rng(seed=42)
    n_features = X_train.shape[1]
    w = rng.uniform(low=0, high=0.1, size=n_features)
    #w = np.zeros(X_train.shape[1])
    for it in range(iterations):
        pred = X_train @ w  # matrixmultiplikation von allen features mit w
        errors = y_train - pred
        # Update Step
        w = w + lr * (X_train.T @ errors)
    return w

def prediction(df_valid, w, mean_train, std_train, features):
    X_valid = df_valid[features].values  # restliche Spalten (Features)
    X_valid = (X_valid - mean_train) / std_train # Werte standardisieren
    X_valid = np.c_[np.ones(len(X_valid)), X_valid] # bias w[0] einfügen

    pred_test = X_valid @ w
    pred_class = np.sign(pred_test)
    return pred_class

def compute_accuracy(y_pred, df_test):
    y_true = df_test['diagnosis'].values
    accuracy = (y_pred == y_true).mean()
    return accuracy

def hyperparameter_tuning(df_train, df_valid, features):
    learning_rates = [0.00005, 0.00009, 0.0001, 0.0005]
    iterations_list = [5, 10, 100, 1000, 10000, 1000000]
    results = []
    best_accur = 0
    best_param = None
    best_model = None

    # Standardisierung hier, einmal für alle Durchläufe
    X, mean_train, std_train = standardisation(df_train, features)

    for lr in learning_rates:
        for it in iterations_list:
            w = gradient_descent(df_train, lr, it, X)
            y_pred = prediction(df_valid, w, mean_train, std_train, features)
            acc = compute_accuracy(y_pred, df_valid)
            print(f"lr={lr}, it={it}, acc={acc:.4f}")

            if acc > best_accur:
                best_param = (lr, it)
                best_accur = acc
                best_model = (w, mean_train, std_train)

            results.append([lr, it, acc])
    return best_model, best_accur, best_param, results

#def final_test(df_test):


if __name__ =="__main__":
    # 1. Daten laden
    df_train = load_data(csv_path_train)
    df_train, df_valid = create_validation_df(df_train)
    df_test = load_data(csv_path_test)

    # 2. deskriptive Datenanalyse
    basic_info(df_train)
    class_distribution(df_train)
    compute_feature_statistics(df_train)
    compute_correlation(df_train)
    boxplot_visualization(df_train)
    compute_scatterplots(df_train)

    # 3. Modell mit Top-7 Features
    print("Modell: Top-7 Features")
    best_model_top7, best_acc_top7, best_param_top7, results_top7 = hyperparameter_tuning(df_train, df_valid, top_features)

    # Top-7 Heatmap
    results_df_top7 = pd.DataFrame(results_top7, columns=["lr", "iterations", "accuracy"])
    pivot_top7 = results_df_top7.pivot(index="lr", columns="iterations", values="accuracy")

    # 4. Modell mit allen Features
    all_features = df_train.drop(columns='diagnosis').columns.tolist()
    print("Modell: Alle Features")
    best_model_all, best_acc_all, best_param_all, results_all = hyperparameter_tuning(df_train, df_valid, all_features)

    # Alle Features Heatmap
    results_df_all = pd.DataFrame(results_all, columns=["lr", "iterations", "accuracy"])
    pivot_all = results_df_all.pivot(index="lr", columns="iterations", values="accuracy")

    # 5. Vergleich
    print(f"Top-7 Accuracy: {best_acc_top7:.4f}")
    print(f"Alle Features Accuracy: {best_acc_all:.4f}")
    print(f"Unterschied: {abs(best_acc_all - best_acc_top7):.4f}")

    # Heatmaps nebeneinander darstellen
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.heatmap(pivot_top7, annot=True, fmt=".4f", cmap="viridis", ax=axes[0])
    axes[0].set_title("Hyperparameter-Tuning: Top-7 Features")

    sns.heatmap(pivot_all, annot=True, fmt=".4f", cmap="viridis", ax=axes[1])
    axes[1].set_title("Hyperparameter-Tuning: Alle Features")

    plt.tight_layout()
    plt.show()



    # Nach dem Hyperparameter-Tuning, das beste Modell speichern
    w, mean_train, std_train = best_model_top7  # oder best_model_all, je nachdem welches besser war

    with open("model.pkl", "wb") as f:
        pickle.dump({
            "w": w,
            "mean_train": mean_train,
            "std_train": std_train
        }, f)

    print("Modell gespeichert!")