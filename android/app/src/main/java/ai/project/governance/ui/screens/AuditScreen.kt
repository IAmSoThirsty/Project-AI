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
import ai.project.governance.data.model.AuditRecord
import ai.project.governance.data.repository.GovernanceRepository
import ai.project.governance.data.repository.Resource
import ai.project.governance.ui.theme.BackgroundDark
import ai.project.governance.ui.theme.GovernancePurple
import ai.project.governance.ui.theme.SurfaceDark
import ai.project.governance.ui.theme.VerdictAllow
import ai.project.governance.ui.theme.VerdictDeny
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

// ViewModel
data class AuditState(
    val audits: List<AuditRecord> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class AuditViewModel @Inject constructor(
    private val repository: GovernanceRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(AuditState())
    val state = _state.asStateFlow()
    
    init {
        loadAudits()
    }
    
    fun loadAudits() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            repository.getAudit(100).collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.value = _state.value.copy(
                            audits = result.data.records,
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
fun AuditScreen(
    navController: NavController,
    viewModel: AuditViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Audit Log") },
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
                    Text(
                        "Immutable audit trail of all governance decisions. Every intent evaluation is cryptographically logged.",
                        modifier = Modifier.padding(16.dp),
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.White.copy(alpha = 0.7f)
                    )
                }
            }
            
            items(state.audits) { audit ->
                AuditLogCard(audit)
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
fun AuditLogCard(audit: AuditRecord) {
    val verdictColor = when (audit.finalVerdict.lowercase()) {
        "allow" -> VerdictAllow
        else -> VerdictDeny
    }
    
    val dateFormat = SimpleDateFormat("MMM dd, yyyy HH:mm:ss", Locale.getDefault())
    val timeStr = dateFormat.format(Date((audit.timestamp * 1000).toLong()))
    
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
                    audit.finalVerdict.uppercase(),
                    fontWeight = FontWeight.Bold,
                    color = verdictColor,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    "TARL ${audit.tarlVersion}",
                    style = MaterialTheme.typography.bodySmall,
                    color = GovernancePurple
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                timeStr,
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.6f)
            )
            
            Text(
                "Hash: ${audit.intentHash.take(16)}...",
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.5f),
                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
            )
        }
    }
}
