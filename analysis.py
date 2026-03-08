import pandas as pd

print("Script started successfully ✅")

# Load data
df = pd.read_csv("data/matches.csv")

# Select opponent
opponent = "NAVI"  # Change this manually

print(f"\nAnalyzing games vs: {opponent}")

# Filter matches
filtered_df = df[df["opponent_team"] == opponent]

if len(filtered_df) == 0:
    print("No games found vs this opponent.")
    exit()

# ---- H2H SUMMARY ----
total_games = len(filtered_df)
wins = len(filtered_df[filtered_df["result"] == "win"])
losses = total_games - wins
winrate = (wins / total_games) * 100

print("\nHead-to-Head Summary:")
print(f"Total games: {total_games}")
print(f"Wins: {wins}")
print(f"Losses: {losses}")
print(f"Winrate: {winrate:.1f}%")

# ---- HERO STATS ----
hero_columns = [
    "our_hero_1",
    "our_hero_2",
    "our_hero_3",
    "our_hero_4",
    "our_hero_5"
]

heroes_df = filtered_df.melt(
    id_vars=["result"],
    value_vars=hero_columns,
    var_name="hero_slot",
    value_name="hero"
)

heroes_df = heroes_df.dropna()

hero_games = heroes_df.groupby("hero").size()
hero_wins = heroes_df[heroes_df["result"] == "win"].groupby("hero").size()

hero_stats = pd.DataFrame({
    "games": hero_games,
    "wins": hero_wins
}).fillna(0)

hero_stats["winrate"] = (hero_stats["wins"] / hero_stats["games"]) * 100
hero_stats = hero_stats.sort_values(by="games", ascending=False)

print("\nHero statistics vs opponent:")
print(hero_stats)