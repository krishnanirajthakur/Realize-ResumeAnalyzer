"""
Missing Section Handling and Dynamic Weight Re-normalization
"""
from typing import Dict, Tuple, List, Set

def renormalize_weights(
    nominal_weights: Dict[str, float], missing_components: Set[str]
) -> Tuple[Dict[str, float], float, List[str]]:
    """
    Re-distribute weights dynamically when certain document sections are missing or undetectable.
    
    Formula:
        For j in Active:
            effective_weight_j = nominal_weight_j / sum(nominal_weight_k for k in Active)
            
    Returns:
        (effective_weights_dict, confidence_percentage, warning_messages)
    """
    active_components = [c for c in nominal_weights if c not in missing_components]
    active_nominal_sum = sum(nominal_weights[c] for c in active_components)
    
    warnings = []
    effective_weights = {}
    
    if not active_components or active_nominal_sum <= 0:
        # Extreme fallback: equal distribution across all components
        count = len(nominal_weights)
        for c in nominal_weights:
            effective_weights[c] = 1.0 / count if count > 0 else 0.0
        confidence = 20.0
        warnings.append("All evaluation criteria were unidentifiable. Baseline default applied.")
        return effective_weights, confidence, warnings
        
    for c in nominal_weights:
        if c in missing_components:
            effective_weights[c] = 0.0
            warnings.append(
                f"Component '{c}' could not be reliably identified from document; nominal weight {nominal_weights[c]}% redistributed."
            )
        else:
            # Re-normalized proportion
            effective_weights[c] = nominal_weights[c] / active_nominal_sum
            
    # Confidence score: fraction of total nominal weight that was present
    total_nominal = sum(nominal_weights.values()) or 100.0
    confidence = round((active_nominal_sum / total_nominal) * 100.0, 1)
    
    return effective_weights, confidence, warnings
