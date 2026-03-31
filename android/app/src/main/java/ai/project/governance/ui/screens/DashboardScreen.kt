package ai.project.governance.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavController
import ai.project.governance.ui.navigation.Screen
import ai.project.governance.ui.theme.*
import ai.project.governance.ui.viewmodel.DashboardViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    navController: NavController,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Project ", fontWeight = FontWeight.Normal)
                        Text("AI", color = GovernancePurple, fontWeight = FontWeight.Bold)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BackgroundDark
                ),
                actions = {
                    IconButton(onClick = { viewModel.loadDashboard() }) {
                        Icon(Icons.Default.Refresh, "Refresh")
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = BackgroundDark
            ) {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Dashboard, "Dashboard") },
                    label = { Text("Dashboard") },
                    selected = true,
                    onClick = { }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.PlayArrow, "Intent") },
                    label = { Text("Submit") },
                    selected = false,
                    onClick = { navController.navigate(Screen.Intent.route) }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.History, "Audit") },
                    label = { Text("Audit") },
                    selected = false,
                    onClick = { navController.navigate(Screen.Audit.route) }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Shield, "TARL") },
                    label = { Text("TARL") },
                    selected = false,
                    onClick = { navController.navigate(Screen.Tarl.route) }
                )
            }
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .background(BackgroundDark)
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Kernel Status Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Governance Kernel",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            Box(
                                modifier = Modifier
                                    .size(12.dp)
                                    .clip(CircleShape)
                                    .background(
                                        if (state.health?.status == "governance-online") 
                                            StatusOnline 
                                        else 
                                            StatusOffline
                                    )
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Text(
                            state.health?.status ?: "Loading...",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White.copy(alpha = 0.7f)
                        )
                        
                        Text(
                            "TARL ${state.health?.tarl ?: "..."}",
                            style = MaterialTheme.typography.bodySmall,
                            color = GovernancePurple
                        )
                    }
                }
            }
            
            // Triumvirate Pillars
            item {
                Text(
                    "Triumvirate Pillars",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    PillarCard(
                        name = "Galahad",
                        role = "Ethics",
                        color = GalahadPurple,
                        modifier = Modifier.weight(1f)
                    )
                    PillarCard(
                        name = "Cerberus",
                        role = "Defense",
                        color = CerberusRed,
                        modifier = Modifier.weight(1f)
                    )
                    PillarCard(
                        name = "Codex",
                        role = "Arbiter",
                        color = CodexDeusGreen,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // Recent Decisions
            item {
                Text(
                    "Recent Decisions",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            items(state.recentAudits.take(5)) { audit ->
                DecisionCard(
                    verdict = audit.finalVerdict,
                    timestamp = audit.timestamp,
                    hash = audit.intentHash
                )
            }
            
            if (state.isLoading) {
                item {
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = GovernancePurple)
                    }
                }
            }
        }
    }
}

@Composable
fun PillarCard(
    name: String,
    role: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(color.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(20.dp)
                        .clip(CircleShape)
                        .background(color)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                role,
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.6f)
            )
        }
    }
}

@Composable
fun DecisionCard(
    verdict: String,
    timestamp: Double,
    hash: String
) {
    val verdictColor = when (verdict.lowercase()) {
        "allow" -> VerdictAllow
        "deny" -> VerdictDeny
        else -> VerdictDegrade
    }
    
    val dateFormat = SimpleDateFormat("MMM dd, HH:mm", Locale.getDefault())
    val timeStr = dateFormat.format(Date((timestamp * 1000).toLong()))
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    verdict.uppercase(),
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold,
                    color = verdictColor
                )
                Text(
                    timeStr,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.White.copy(alpha = 0.6f)
                )
            }
            Text(
                hash.take(8) + "...",
                style = MaterialTheme.typography.bodySmall,
                color = GovernancePurple,
                fontWeight = FontWeight.Mono
            )
        }
    }
}
