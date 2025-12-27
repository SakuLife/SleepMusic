import google.generativeai as genai


def generate_image_variations(api_key, model, season_jp, season_en, mood_jp, mood_en):
    """
    Generate unique image prompt variations using Gemini AI.

    Returns:
        tuple: (bg_variation, thumb_variation) - Two different variation phrases
    """
    if not api_key:
        # Fallback: return simple variations if no API key
        return "星空の夜、starry night", "美しい夜空、beautiful night sky"

    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel(model)

    prompt = f"""あなたは睡眠用BGM動画の画像プロンプト生成AIです。

季節: {season_jp} / {season_en}
ムード: {mood_jp} / {mood_en}

上記の季節とムードに合った、星空をベースにした睡眠導入用の画像バリエーション要素を2つ生成してください。

要件:
- 各バリエーションは日本語と英語を含む短いフレーズ（10-15単語程度）
- 星空の風景に追加する具体的な視覚要素を記述（例: 流れ星、霧、山、湖など）
- 2つのバリエーションは互いに異なる要素を含むこと
- 睡眠導入に適した静かで落ち着いた雰囲気
- 季節感を反映した要素を含める

出力形式（この2行のみ、説明なし）:
バリエーション1の日本語、バリエーション1の英語
バリエーション2の日本語、バリエーション2の英語"""

    try:
        response = llm.generate_content(prompt)
        lines = response.text.strip().split('\n')

        if len(lines) >= 2:
            bg_variation = lines[0].strip()
            thumb_variation = lines[1].strip()
            return bg_variation, thumb_variation
        else:
            # Fallback if response format is unexpected
            return "星空の夜、starry night", "美しい夜空、beautiful night sky"

    except Exception as e:
        print(f"Warning: Gemini API failed ({e}), using fallback variations")
        return "星空の夜、starry night", "美しい夜空、beautiful night sky"
