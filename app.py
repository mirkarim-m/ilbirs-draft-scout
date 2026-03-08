import os
import uuid
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ilbirs Draft Scout", layout="wide")

MATCHES_FILE = "data/matches.csv"
DRAFT_ACTIONS_FILE = "data/draft_actions.csv"

HEROES = sorted([
    "Abaddon", "Alchemist", "Ancient Apparition", "Anti-Mage", "Arc Warden", "Axe",
    "Bane", "Batrider", "Beastmaster", "Bloodseeker", "Bounty Hunter", "Brewmaster",
    "Bristleback", "Broodmother", "Centaur Warrunner", "Chaos Knight", "Chen", "Clinkz",
    "Clockwerk", "Crystal Maiden", "Dark Seer", "Dark Willow", "Dawnbreaker", "Dazzle",
    "Death Prophet", "Disruptor", "Doom", "Dragon Knight", "Drow Ranger", "Earth Spirit",
    "Earthshaker", "Elder Titan", "Ember Spirit", "Enchantress", "Enigma", "Faceless Void",
    "Grimstroke", "Gyrocopter", "Hoodwink", "Huskar", "Invoker", "Io", "Jakiro",
    "Juggernaut", "Kez", "Keeper of the Light", "Kunkka", "Largo", "Legion Commander", "Leshrac",
    "Lich", "Lifestealer", "Lina", "Lion", "Lone Druid", "Luna", "Lycan", "Magnus",
    "Marci", "Mars", "Medusa", "Meepo", "Mirana", "Monkey King", "Morphling", "Muerta",
    "Naga Siren", "Nature's Prophet", "Necrophos", "Night Stalker", "Nyx Assassin",
    "Ogre Magi", "Omniknight", "Oracle", "Outworld Destroyer", "Pangolier",
    "Phantom Assassin", "Phantom Lancer", "Phoenix", "Primal Beast", "Puck", "Pudge",
    "Pugna", "Queen of Pain", "Razor", "Riki", "Ringmaster", "Rubick", "Sand King",
    "Shadow Demon", "Shadow Fiend", "Shadow Shaman", "Silencer", "Skywrath Mage",
    "Slardar", "Slark", "Snapfire", "Sniper", "Spectre", "Spirit Breaker", "Storm Spirit",
    "Sven", "Techies", "Templar Assassin", "Terrorblade", "Tidehunter", "Timbersaw",
    "Tinker", "Tiny", "Treant Protector", "Troll Warlord", "Tusk", "Underlord",
    "Undying", "Ursa", "Vengeful Spirit", "Venomancer", "Viper", "Visage", "Void Spirit",
    "Warlock", "Weaver", "Windranger", "Winter Wyvern", "Witch Doctor", "Wraith King",
    "Zeus"
])

DRAFT_SEQUENCE = [
    {"action_number": 1,  "phase": 1, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 2,  "phase": 1, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 3,  "phase": 1, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 4,  "phase": 1, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 5,  "phase": 1, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 6,  "phase": 1, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 7,  "phase": 1, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 8,  "phase": 2, "action_type": "pick", "draft_side": "first"},
    {"action_number": 9,  "phase": 2, "action_type": "pick", "draft_side": "second"},
    {"action_number": 10, "phase": 3, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 11, "phase": 3, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 12, "phase": 3, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 13, "phase": 4, "action_type": "pick", "draft_side": "second"},
    {"action_number": 14, "phase": 4, "action_type": "pick", "draft_side": "first"},
    {"action_number": 15, "phase": 4, "action_type": "pick", "draft_side": "first"},
    {"action_number": 16, "phase": 4, "action_type": "pick", "draft_side": "second"},
    {"action_number": 17, "phase": 4, "action_type": "pick", "draft_side": "second"},
    {"action_number": 18, "phase": 4, "action_type": "pick", "draft_side": "first"},
    {"action_number": 19, "phase": 5, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 20, "phase": 5, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 21, "phase": 5, "action_type": "ban",  "draft_side": "second"},
    {"action_number": 22, "phase": 5, "action_type": "ban",  "draft_side": "first"},
    {"action_number": 23, "phase": 6, "action_type": "pick", "draft_side": "first"},
    {"action_number": 24, "phase": 6, "action_type": "pick", "draft_side": "second"},
]


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .section-ban {
            background-color: rgba(220, 53, 69, 0.10);
            border-left: 5px solid #dc3545;
            padding: 10px 14px;
            border-radius: 10px;
            margin: 8px 0 12px 0;
            font-weight: 600;
        }
        .section-pick {
            background-color: rgba(40, 167, 69, 0.10);
            border-left: 5px solid #28a745;
            padding: 10px 14px;
            border-radius: 10px;
            margin: 8px 0 12px 0;
            font-weight: 600;
        }
        .mini-card {
            background-color: rgba(255,255,255,0.03);
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .our-label {
            color: #4da3ff;
            font-weight: 700;
        }
        .opp-label {
            color: #ff8c42;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_file_exists(path: str, columns: list[str]) -> None:
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def load_matches() -> pd.DataFrame:
    ensure_file_exists(
        MATCHES_FILE,
        [
            "match_id",
            "date",
            "our_team",
            "opponent_team",
            "result",
            "first_pick_side",
            "patch",
            "tournament",
        ],
    )
    df = pd.read_csv(MATCHES_FILE)
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def load_draft_actions() -> pd.DataFrame:
    ensure_file_exists(
        DRAFT_ACTIONS_FILE,
        ["match_id", "action_number", "phase", "action_type", "draft_side", "team_side", "hero"],
    )
    return pd.read_csv(DRAFT_ACTIONS_FILE)


def save_match(match_row: dict) -> None:
    matches_df = load_matches()
    matches_df = pd.concat([matches_df, pd.DataFrame([match_row])], ignore_index=True)
    matches_df.to_csv(MATCHES_FILE, index=False)


def save_draft_actions(actions: list[dict]) -> None:
    actions_df = load_draft_actions()
    actions_df = pd.concat([actions_df, pd.DataFrame(actions)], ignore_index=True)
    actions_df.to_csv(DRAFT_ACTIONS_FILE, index=False)


def resolve_team_side(first_pick_side: str, draft_side: str) -> str:
    if first_pick_side == "our":
        return "our" if draft_side == "first" else "opp"
    return "opp" if draft_side == "first" else "our"


def extract_match_heroes(actions_df: pd.DataFrame, team_side: str, action_type: str) -> list[str]:
    filtered = actions_df[
        (actions_df["team_side"] == team_side)
        & (actions_df["action_type"] == action_type)
        & (actions_df["hero"].notna())
    ].sort_values("action_number")
    return filtered["hero"].tolist()


def phase_title(phase_number: int) -> str:
    if phase_number in [1, 3, 5]:
        return f"Phase {phase_number} — Bans"
    return f"Phase {phase_number} — Picks"


def reset_draft_inputs() -> None:
    for step in DRAFT_SEQUENCE:
        key = f"draft_action_{step['action_number']}"
        if key in st.session_state:
            del st.session_state[key]


def get_selected_heroes() -> list[str]:
    selected = []
    for step in DRAFT_SEQUENCE:
        value = st.session_state.get(f"draft_action_{step['action_number']}", "-")
        if value != "-":
            selected.append(value)
    return selected


def render_hero_selectbox(action_number: int, label: str) -> str:
    key = f"draft_action_{action_number}"
    current_value = st.session_state.get(key, "-")

    already_selected = []
    for step in DRAFT_SEQUENCE:
        other_key = f"draft_action_{step['action_number']}"
        if other_key == key:
            continue
        value = st.session_state.get(other_key, "-")
        if value != "-":
            already_selected.append(value)

    available_heroes = [hero for hero in HEROES if hero not in already_selected]

    if current_value != "-" and current_value not in available_heroes:
        available_heroes = [current_value] + available_heroes

    options = ["-"] + available_heroes

    if current_value not in options:
        current_value = "-"

    current_index = options.index(current_value)

    return st.selectbox(label=label, options=options, index=current_index, key=key)


def calculate_pick_stats(
    matches_df: pd.DataFrame,
    draft_df: pd.DataFrame,
    selected_opponent: str,
    team_side: str,
) -> pd.DataFrame:
    opponent_matches = matches_df[matches_df["opponent_team"] == selected_opponent]
    if opponent_matches.empty:
        return pd.DataFrame(columns=["hero", "games", "wins", "winrate"])

    match_ids = opponent_matches["match_id"].tolist()

    picks_df = draft_df[
        (draft_df["match_id"].isin(match_ids))
        & (draft_df["team_side"] == team_side)
        & (draft_df["action_type"] == "pick")
        & (draft_df["hero"].notna())
    ].copy()

    if picks_df.empty:
        return pd.DataFrame(columns=["hero", "games", "wins", "winrate"])

    result_map = matches_df.set_index("match_id")["result"].to_dict()
    picks_df["match_result"] = picks_df["match_id"].map(result_map)

    win_result = "win" if team_side == "our" else "lose"

    games = picks_df.groupby("hero").size()
    wins = picks_df[picks_df["match_result"] == win_result].groupby("hero").size()

    stats = pd.DataFrame({"games": games, "wins": wins}).fillna(0)
    stats["wins"] = stats["wins"].astype(int)
    stats["winrate"] = (stats["wins"] / stats["games"]) * 100
    stats = stats.reset_index().sort_values(by=["games", "winrate"], ascending=[False, False])

    return stats


def calculate_action_stats(
    matches_df: pd.DataFrame,
    draft_df: pd.DataFrame,
    selected_opponent: str,
    team_side: str,
    action_type: str,
    action_numbers: list[int] | None = None,
    phases: list[int] | None = None,
) -> pd.DataFrame:
    opponent_matches = matches_df[matches_df["opponent_team"] == selected_opponent]
    if opponent_matches.empty:
        return pd.DataFrame(columns=["hero", "games", "wins", "winrate"])

    match_ids = opponent_matches["match_id"].tolist()

    actions = draft_df[
        (draft_df["match_id"].isin(match_ids))
        & (draft_df["team_side"] == team_side)
        & (draft_df["action_type"] == action_type)
        & (draft_df["hero"].notna())
    ].copy()

    if action_numbers is not None:
        actions = actions[actions["action_number"].isin(action_numbers)]

    if phases is not None:
        actions = actions[actions["phase"].isin(phases)]

    if actions.empty:
        return pd.DataFrame(columns=["hero", "games", "wins", "winrate"])

    result_map = matches_df.set_index("match_id")["result"].to_dict()
    actions["match_result"] = actions["match_id"].map(result_map)

    win_result = "win" if team_side == "our" else "lose"

    games = actions.groupby("hero").size()
    wins = actions[actions["match_result"] == win_result].groupby("hero").size()

    stats = pd.DataFrame({"games": games, "wins": wins}).fillna(0)
    stats["wins"] = stats["wins"].astype(int)
    stats["winrate"] = (stats["wins"] / stats["games"]) * 100
    stats = stats.reset_index().sort_values(by=["games", "winrate"], ascending=[False, False])

    return stats


def calculate_last_pick_stats(
    matches_df: pd.DataFrame,
    draft_df: pd.DataFrame,
    selected_opponent: str,
    team_side: str,
) -> pd.DataFrame:
    opponent_matches = matches_df[matches_df["opponent_team"] == selected_opponent]
    if opponent_matches.empty:
        return pd.DataFrame(columns=["hero", "games", "wins", "winrate"])

    match_ids = opponent_matches["match_id"].tolist()

    picks = draft_df[
        (draft_df["match_id"].isin(match_ids))
        & (draft_df["team_side"] == team_side)
        & (draft_df["action_type"] == "pick")
        & (draft_df["hero"].notna())
    ].copy()

    if picks.empty:
        return pd.DataFrame(columns=["hero", "games", "wins", "winrate"])

    last_picks = (
        picks.sort_values(["match_id", "action_number"])
        .groupby("match_id", as_index=False)
        .tail(1)
        .copy()
    )

    result_map = matches_df.set_index("match_id")["result"].to_dict()
    last_picks["match_result"] = last_picks["match_id"].map(result_map)

    win_result = "win" if team_side == "our" else "lose"

    games = last_picks.groupby("hero").size()
    wins = last_picks[last_picks["match_result"] == win_result].groupby("hero").size()

    stats = pd.DataFrame({"games": games, "wins": wins}).fillna(0)
    stats["wins"] = stats["wins"].astype(int)
    stats["winrate"] = (stats["wins"] / stats["games"]) * 100
    stats = stats.reset_index().sort_values(by=["games", "winrate"], ascending=[False, False])

    return stats


def render_phase_header(phase_number: int) -> None:
    if phase_number in [1, 3, 5]:
        st.markdown(
            f'<div class="section-ban">{phase_title(phase_number)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="section-pick">{phase_title(phase_number)}</div>',
            unsafe_allow_html=True,
        )


inject_custom_css()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Match"])

if page == "Dashboard":
    st.title("Ilbirs Draft Scout")
    st.subheader("Draft-aware dashboard")

    matches_df = load_matches()
    draft_df = load_draft_actions()

    if matches_df.empty:
        st.warning("No match data found yet. Please add matches first.")
        st.stop()

    opponents = sorted(matches_df["opponent_team"].dropna().unique())
    selected_opponent = st.selectbox("Select opponent", opponents)

    filtered_matches = matches_df[matches_df["opponent_team"] == selected_opponent].copy()

    if filtered_matches.empty:
        st.warning("No matches found for this opponent.")
        st.stop()

    st.subheader("Filters")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        first_pick_filter = st.selectbox(
            "First pick side",
            options=["All", "Our team", "Opponent"],
            index=0,
        )

    with f2:
        available_patches = sorted([p for p in filtered_matches["patch"].dropna().unique() if str(p).strip() != ""])
        patch_filter = st.selectbox("Patch", ["All"] + available_patches if available_patches else ["All"])

    with f3:
        available_tournaments = sorted([t for t in filtered_matches["tournament"].dropna().unique() if str(t).strip() != ""])
        tournament_filter = st.selectbox("Tournament", ["All"] + available_tournaments if available_tournaments else ["All"])

    with f4:
        min_date = filtered_matches["date"].min()
        max_date = filtered_matches["date"].max()

        if pd.isna(min_date) or pd.isna(max_date):
            start_date = None
            end_date = None
            st.write("No valid dates")
        else:
            start_date, end_date = st.date_input(
                "Date range",
                value=(min_date.date(), max_date.date()),
            )

    if first_pick_filter == "Our team":
        filtered_matches = filtered_matches[filtered_matches["first_pick_side"] == "our"]
    elif first_pick_filter == "Opponent":
        filtered_matches = filtered_matches[filtered_matches["first_pick_side"] == "opp"]

    if patch_filter != "All":
        filtered_matches = filtered_matches[filtered_matches["patch"] == patch_filter]

    if tournament_filter != "All":
        filtered_matches = filtered_matches[filtered_matches["tournament"] == tournament_filter]

    if not filtered_matches.empty and start_date and end_date:
        filtered_matches = filtered_matches[
            (filtered_matches["date"].dt.date >= start_date)
            & (filtered_matches["date"].dt.date <= end_date)
        ]

    if filtered_matches.empty:
        st.warning("No matches found after applying filters.")
        st.stop()

    total_games = len(filtered_matches)
    wins = len(filtered_matches[filtered_matches["result"] == "win"])
    losses = total_games - wins
    winrate = (wins / total_games) * 100 if total_games > 0 else 0

    st.subheader("Head-to-Head Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Games", total_games)
    c2.metric("Wins", wins)
    c3.metric("Losses", losses)
    c4.metric("Winrate", f"{winrate:.1f}%")

    filtered_match_ids = filtered_matches["match_id"].tolist()
    filtered_draft_df = draft_df[draft_df["match_id"].isin(filtered_match_ids)].copy()

    st.subheader("Our Pick Stats vs Opponent")
    our_pick_stats = calculate_pick_stats(filtered_matches, filtered_draft_df, selected_opponent, "our")
    if not our_pick_stats.empty:
        st.dataframe(our_pick_stats, width="stretch")
        st.bar_chart(our_pick_stats.set_index("hero")["winrate"])
    else:
        st.write("No our-pick data found.")

    st.subheader("Opponent Pick Stats vs Opponent")
    opp_pick_stats = calculate_pick_stats(filtered_matches, filtered_draft_df, selected_opponent, "opp")
    if not opp_pick_stats.empty:
        st.dataframe(opp_pick_stats, width="stretch")
        st.bar_chart(opp_pick_stats.set_index("hero")["winrate"])
    else:
        st.write("No opponent-pick data found.")

    st.subheader("Phase 1 Bans Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Our Phase 1 Bans")
        our_phase1_bans = calculate_action_stats(
            filtered_matches, filtered_draft_df, selected_opponent, "our", "ban", phases=[1]
        )
        if not our_phase1_bans.empty:
            st.dataframe(our_phase1_bans, width="stretch")
        else:
            st.write("No our Phase 1 bans found.")

    with col2:
        st.write("### Opponent Phase 1 Bans")
        opp_phase1_bans = calculate_action_stats(
            filtered_matches, filtered_draft_df, selected_opponent, "opp", "ban", phases=[1]
        )
        if not opp_phase1_bans.empty:
            st.dataframe(opp_phase1_bans, width="stretch")
        else:
            st.write("No opponent Phase 1 bans found.")

    st.subheader("First Pick Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Our First Picks")
        our_first_picks = calculate_action_stats(
            filtered_matches, filtered_draft_df, selected_opponent, "our", "pick", action_numbers=[8]
        )
        if not our_first_picks.empty:
            st.dataframe(our_first_picks, width="stretch")
        else:
            st.write("No our first picks found.")

    with col2:
        st.write("### Opponent First Picks")
        opp_first_picks = calculate_action_stats(
            filtered_matches, filtered_draft_df, selected_opponent, "opp", "pick", action_numbers=[8]
        )
        if not opp_first_picks.empty:
            st.dataframe(opp_first_picks, width="stretch")
        else:
            st.write("No opponent first picks found.")

    st.subheader("Last Pick Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Our Last Picks")
        our_last_picks = calculate_last_pick_stats(filtered_matches, filtered_draft_df, selected_opponent, "our")
        if not our_last_picks.empty:
            st.dataframe(our_last_picks, width="stretch")
        else:
            st.write("No our last picks found.")

    with col2:
        st.write("### Opponent Last Picks")
        opp_last_picks = calculate_last_pick_stats(filtered_matches, filtered_draft_df, selected_opponent, "opp")
        if not opp_last_picks.empty:
            st.dataframe(opp_last_picks, width="stretch")
        else:
            st.write("No opponent last picks found.")

    st.subheader("Match History")
    display_matches = filtered_matches.copy()
    if "date" in display_matches.columns:
        display_matches["date"] = display_matches["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_matches, width="stretch")

    selected_match_id = st.selectbox(
        "Select match to inspect draft",
        filtered_matches["match_id"].tolist(),
    )
if st.button("Delete this match", type="secondary"):
    # Delete match row
    matches_df = load_matches()
    matches_df = matches_df[matches_df["match_id"] != selected_match_id]
    matches_df.to_csv(MATCHES_FILE, index=False)

    # Delete draft actions
    draft_df = load_draft_actions()
    draft_df = draft_df[draft_df["match_id"] != selected_match_id]
    draft_df.to_csv(DRAFT_ACTIONS_FILE, index=False)

    st.success("Match deleted successfully.")
    st.rerun()
    selected_actions = filtered_draft_df[filtered_draft_df["match_id"] == selected_match_id].copy()

    if not selected_actions.empty:
        selected_actions = selected_actions.sort_values("action_number")

        st.subheader("Draft Order")
        st.dataframe(selected_actions, width="stretch")

        our_picks = extract_match_heroes(selected_actions, "our", "pick")
        opp_picks = extract_match_heroes(selected_actions, "opp", "pick")
        our_bans = extract_match_heroes(selected_actions, "our", "ban")
        opp_bans = extract_match_heroes(selected_actions, "opp", "ban")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Our Picks")
            st.write(", ".join(our_picks) if our_picks else "No picks found.")
            st.write("### Our Bans")
            st.write(", ".join(our_bans) if our_bans else "No bans found.")

        with col2:
            st.write("### Opponent Picks")
            st.write(", ".join(opp_picks) if opp_picks else "No picks found.")
            st.write("### Opponent Bans")
            st.write(", ".join(opp_bans) if opp_bans else "No bans found.")

if page == "Add Match":
    st.title("Add Match")
    st.subheader("Enter match info and full draft order")

    first_pick_side = st.selectbox(
        "Who had first pick?",
        options=["our", "opp"],
        format_func=lambda x: "Our team" if x == "our" else "Opponent",
        key="first_pick_side_selector",
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        date = st.date_input("Match date")
        our_team = st.text_input("Our team", value="Ilbirs")
        opponent_team = st.text_input("Opponent team")
        result = st.selectbox("Result", ["win", "lose"])

    with col_right:
        patch = st.text_input("Patch", placeholder="e.g. 7.39b")
        tournament = st.text_input("Tournament", placeholder="e.g. EPL / Scrim / Qualifier")
        st.write("")
        if st.button("Reset draft inputs", width="stretch"):
            reset_draft_inputs()
            st.rerun()

    st.write("## Draft by Phases")

    action_inputs = []

    for phase in [1, 2, 3, 4, 5, 6]:
        phase_actions = [step for step in DRAFT_SEQUENCE if step["phase"] == phase]

        with st.expander(phase_title(phase), expanded=True):
            render_phase_header(phase)

            left_col, right_col = st.columns(2)

            our_phase_actions = []
            opp_phase_actions = []

            for step in phase_actions:
                team_side = resolve_team_side(first_pick_side, step["draft_side"])
                if team_side == "our":
                    our_phase_actions.append(step)
                else:
                    opp_phase_actions.append(step)

            with left_col:
                st.markdown('<div class="our-label">Our team</div>', unsafe_allow_html=True)
                for step in our_phase_actions:
                    action_number = step["action_number"]
                    action_type = step["action_type"]

                    hero = render_hero_selectbox(
                        action_number=action_number,
                        label=f"#{action_number} | {action_type.upper()}"
                    )

                    action_inputs.append({
                        "action_number": action_number,
                        "phase": phase,
                        "action_type": action_type,
                        "draft_side": step["draft_side"],
                        "team_side": "our",
                        "hero": None if hero == "-" else hero,
                    })

            with right_col:
                st.markdown('<div class="opp-label">Opponent</div>', unsafe_allow_html=True)
                for step in opp_phase_actions:
                    action_number = step["action_number"]
                    action_type = step["action_type"]

                    hero = render_hero_selectbox(
                        action_number=action_number,
                        label=f"#{action_number} | {action_type.upper()}"
                    )

                    action_inputs.append({
                        "action_number": action_number,
                        "phase": phase,
                        "action_type": action_type,
                        "draft_side": step["draft_side"],
                        "team_side": "opp",
                        "hero": None if hero == "-" else hero,
                    })

    selected_heroes = get_selected_heroes()
    st.write(f"Selected unique heroes: {len(selected_heroes)}")

    if st.button("Save Match", type="primary", width="stretch"):
        if not opponent_team.strip():
            st.error("Opponent team is required.")
        else:
            match_id = str(uuid.uuid4())[:8]

            match_row = {
                "match_id": match_id,
                "date": str(date),
                "our_team": our_team.strip(),
                "opponent_team": opponent_team.strip(),
                "result": result,
                "first_pick_side": first_pick_side,
                "patch": patch.strip(),
                "tournament": tournament.strip(),
            }

            actions_to_save = []
            for action in sorted(action_inputs, key=lambda x: x["action_number"]):
                actions_to_save.append({
                    "match_id": match_id,
                    "action_number": action["action_number"],
                    "phase": action["phase"],
                    "action_type": action["action_type"],
                    "draft_side": action["draft_side"],
                    "team_side": action["team_side"],
                    "hero": action["hero"],
                })

            save_match(match_row)
            save_draft_actions(actions_to_save)

            st.success(f"Match saved successfully. Match ID: {match_id}")
