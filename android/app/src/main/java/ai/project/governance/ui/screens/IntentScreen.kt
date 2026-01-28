package ai.project.governance.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavController
import ai.project.governance.data.model.ActorType
import ai.project.governance.data.model.ActionType
import ai.project.governance.ui.theme.*
import ai.project.governance.ui.viewmodel.IntentViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IntentScreen(
    navController: NavController,
    viewModel: IntentViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Submit Intent") },
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(BackgroundDark)
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Info Card
            Card(
                colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    "Submit an intent for Triumvirate evaluation. All requests pass through TARL governance.",
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White.copy(alpha = 0.7f)
                )
            }
            
            // Actor Selection
            Text("Actor Type", fontWeight = FontWeight.Bold)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ActorType.values().forEach { actor ->
                    FilterChip(
                        selected = state.actor == actor,
                        onClick = { viewModel.updateActor(actor) },
                        label = { Text(actor.name.lowercase().capitalize()) },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // Action Selection
            Text("Action Type", fontWeight = FontWeight.Bold)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ActionType.values().forEach { action ->
                    FilterChip(
                        selected = state.action == action,
                        onClick = { viewModel.updateAction(action) },
                        label = { Text(action.name.lowercase().capitalize()) },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // Target Input
            Text("Target Resource", fontWeight = FontWeight.Bold)
            OutlinedTextField(
                value = state.target,
                onValueChange = { viewModel.updateTarget(it) },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("/path/to/resource") },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = GovernancePurple,
                    unfocusedBorderColor = Color.White.copy(alpha = 0.3f)
                )
            )
            
            // Submit Button
            Button(
                onClick = { viewModel.submitIntent() },
                modifier = Modifier.fillMaxWidth(),
                enabled = state.target.isNotBlank() && !state.isLoading,
                colors = ButtonDefaults.buttonColors(
                    containerColor = GovernancePurple
                )
            ) {
                if (state.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = Color.White
                    )
                } else {
                    Icon(Icons.Default.Send, "Submit")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Submit Intent")
                }
            }
            
            // Result Display
            state.result?.let { result ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (result.governance.finalVerdict.name == "ALLOW") 
                            VerdictAllow.copy(alpha = 0.2f)
                        else 
                            VerdictDeny.copy(alpha = 0.2f)
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            "Governance Result",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Text(
                            "Verdict: ${result.governance.finalVerdict.name}",
                            fontWeight = FontWeight.Bold,
                            color = if (result.governance.finalVerdict.name == "ALLOW") 
                                VerdictAllow 
                            else 
                                VerdictDeny
                        )
                        
                        Text(
                            "Hash: ${result.governance.intentHash.take(16)}...",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.White.copy(alpha = 0.6f)
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            "Pillar Votes:",
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        
                        result.governance.votes.forEach { vote ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    vote.pillar,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = when (vote.pillar) {
                                        "Galahad" -> GalahadPurple
                                        "Cerberus" -> CerberusRed
                                        else -> CodexDeusGreen
                                    }
                                )
                                Text(
                                    vote.verdict.name,
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                            Text(
                                vote.reason,
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.White.copy(alpha = 0.6f)
                            )
                        }
                    }
                }
            }
            
            // Error Display
            state.error?.let { error ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = VerdictDeny.copy(alpha = 0.2f)
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        error,
                        modifier = Modifier.padding(16.dp),
                        color = VerdictDeny
                    )
                }
            }
        }
    }
}

private fun String.capitalize() = replaceFirstChar { 
    if (it.isLowerCase()) it.titlecase() else it.toString() 
}
