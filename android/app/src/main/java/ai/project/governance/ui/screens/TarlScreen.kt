package ai.project.governance.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.navigation.NavController
import ai.project.governance.data.model.TarlRule
import ai.project.governance.data.repository.GovernanceRepository
import ai.project.governance.data.repository.Resource
import ai.project.governance.ui.theme.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

// ViewModel
data class TarlState(
    val rules: List<TarlRule> = emptyList(),
    val version: String = "",
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class TarlViewModel @Inject constructor(
    private val repository: GovernanceRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(TarlState())
    val state = _state.asStateFlow()
    
    init {
        loadTarl()
    }
    
    fun loadTarl() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            repository.getTarl().collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.value = _state.value.copy(
                            rules = result.data.rules,
                            version = result.data.version,
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
}

// Screen
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TarlScreen(
    navController: NavController,
    viewModel: TarlViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("TARL Governance") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BackgroundDark
                )
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .background(BackgroundDark)
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            "Trust & Authorization Runtime Layer",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "Version ${state.version}",
                            color = GovernancePurple,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "TARL defines the governance rules that all intents must satisfy. These rules are immutable and cryptographically signed.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White.copy(alpha = 0.7f)
                        )
                    }
                }
            }
            
            items(state.rules) { rule ->
                TarlRuleCard(rule)
            }
            
            if (state.isLoading) {
                item {
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = androidx.compose.ui.Alignment.Center
                    ) {
                        CircularProgressIndicator(color = GovernancePurple)
                    }
                }
            }
        }
    }
}

@Composable
fun TarlRuleCard(rule: TarlRule) {
    val riskColor = when (rule.risk.lowercase()) {
        "low" -> VerdictAllow
        "medium" -> VerdictDegrade
        "high", "critical" -> VerdictDeny
        else -> Color.Gray
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    rule.action.uppercase(),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Surface(
                    color = riskColor.copy(alpha = 0.2f),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        rule.risk.uppercase(),
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = riskColor,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                "Allowed Actors:",
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.bodyMedium
            )
            if (rule.allowedActors.isEmpty()) {
                Text(
                    "None (Always denied)",
                    style = MaterialTheme.typography.bodySmall,
                    color = VerdictDeny
                )
            } else {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    rule.allowedActors.forEach { actor ->
                        Surface(
                            color = GovernancePurple.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(6.dp)
                        ) {
                            Text(
                                actor,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                style = MaterialTheme.typography.labelSmall,
                                color = GovernancePurple
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                "Default Verdict: ${rule.default.uppercase()}",
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.6f)
            )
        }
    }
}
