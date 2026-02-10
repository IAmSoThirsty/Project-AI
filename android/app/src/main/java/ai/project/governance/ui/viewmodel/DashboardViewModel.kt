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

data class DashboardState(
    val health: HealthResponse? = null,
    val tarl: TarlResponse? = null,
    val recentAudits: List<AuditRecord> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: GovernanceRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(DashboardState())
    val state = _state.asStateFlow()
    
    init {
        loadDashboard()
    }
    
    fun loadDashboard() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            
            // Load health
            repository.getHealth().collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.value = _state.value.copy(health = result.data)
                    }
                    is Resource.Error -> {
                        _state.value = _state.value.copy(error = result.message)
                    }
                    is Resource.Loading -> {}
                }
            }
            
            // Load TARL
            repository.getTarl().collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.value = _state.value.copy(tarl = result.data)
                    }
                    is Resource.Error -> {}
                    is Resource.Loading -> {}
                }
            }
            
            // Load recent audits
            repository.getAudit(10).collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.value = _state.value.copy(
                            recentAudits = result.data.records,
isLoading = false
                        )
                    }
                    is Resource.Error -> {
                        _state.value = _state.value.copy(isLoading = false)
                    }
                    is Resource.Loading -> {}
                }
            }
        }
    }
}
