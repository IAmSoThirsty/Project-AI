package ai.project.governance.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import ai.project.governance.data.model.*
import ai.project.governance.data.repository.GovernanceRepository
import ai.project.governance.data.repository.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class IntentState(
    val actor: ActorType = ActorType.HUMAN,
    val action: ActionType = ActionType.READ,
    val target: String = "",
    val result: IntentResponse? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class IntentViewModel @Inject constructor(
    private val repository: GovernanceRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(IntentState())
    val state = _state.asStateFlow()
    
    fun updateActor(actor: ActorType) {
        _state.value = _state.value.copy(actor = actor)
    }
    
    fun updateAction(action: ActionType) {
        _state.value = _state.value.copy(action = action)
    }
    
    fun updateTarget(target: String) {
        _state.value = _state.value.copy(target = target)
    }
    
    fun submitIntent() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null, result = null)
            
            val intent = Intent(
                actor = _state.value.actor,
                action = _state.value.action,
                target = _state.value.target,
                origin = "android_app"
            )
            
            repository.submitIntent(intent).collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.value = _state.value.copy(
                            result = result.data,
                            isLoading = false
                        )
                    }
                    is Resource.Error -> {
                        _state.value = _state.value.copy(
                            error = result.message,
                            isLoading = false
                        )
                    }
                    is Resource.Loading -> {}
                }
            }
        }
    }
    
    fun clearResult() {
        _state.value = _state.value.copy(result = null, error = null)
    }
}
