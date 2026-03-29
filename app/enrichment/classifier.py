import re
from typing import Dict, Any

BUSINESS_CATEGORIES = [
  "médico", "doctor", "clínica", "dental", "dentista", "odontólogo",
  "abogado", "asesoría", "gestoría", "notaría",
  "inmobiliaria", "agencia inmobiliaria", "agente inmobiliario",
  "fisioterapeuta", "psicólogo", "óptica", "veterinario", "farmacia",
  "peluquería", "salón de belleza", "estética", "spa", "barbería",
  "fontanero", "electricista", "cerrajero", "taller", "mecánico",
  "academia", "formación", "autoescuela",
  "reformas", "construcción", "arquitecto",
  "restaurante", "bar", "cafetería", "catering",
  "hotel", "alojamiento"
]

class Classifier:
    def classify(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Lead Score and generates Context based on profile data.
        Returns dict with 'score', 'category', 'context'
        """
        score = 0
        detected_category = None
        bio = (profile_data.get('biography') or '').lower()
        business_cat = (profile_data.get('business_category_name') or '').lower()
        
        # Scoring Rules
        if profile_data.get('business_email'):
            score += 40
            
        if profile_data.get('is_business_account'):
            score += 20
            
        # Category Matching
        for keyword in BUSINESS_CATEGORIES:
            if keyword in bio or keyword in business_cat:
                score += 15
                detected_category = keyword
                break
                
        if business_cat in BUSINESS_CATEGORIES:
            score += 10
            
        # Follower rules
        follower_count = profile_data.get('follower_count', 0)
        if 200 <= follower_count <= 50000:
            score += 5
        elif follower_count < 50 or follower_count > 500000:
            score -= 30
            
        # Website rules
        ext_url = profile_data.get('external_url')
        if not ext_url:
            score += 10
        else:
            if 'linktr.ee' in ext_url.lower():
                score -= 10 # Slightly penalize link trees compared to no web, but not as much as pro web
            else:
                score -= 20 # Has professional web
                
        # Bound score 0-100
        score = max(0, min(100, score))
        
        # Context Generation
        context_parts = []
        if ext_url:
            context_parts.append("Tiene web externa")
        else:
            context_parts.append("Sin web propia")
            
        count_k = follower_count / 1000.0 if follower_count >= 1000 else follower_count
        unit = "K" if follower_count >= 1000 else ""
        context_parts.append(f"{count_k:.1f}{unit} seguidores")
        
        if profile_data.get('is_business_account'):
            context_parts.append("cuenta de empresa activa en IG")
            
        if profile_data.get('business_phone'):
            context_parts.append("teléfono visible en bio")
            
        if detected_category:
            context_parts.append(f"categoría detectada: {detected_category}")
            
        return {
            "score": score,
            "category": detected_category,
            "context": ", ".join(context_parts)
        }
