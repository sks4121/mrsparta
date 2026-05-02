def generate_plan(profile):
    calories = profile.weight * 15

    return {
        "calories": calories,
        "protein": profile.weight * 2,
        "carbs": profile.weight * 3,
        "fats": profile.weight * 0.8,
    }   