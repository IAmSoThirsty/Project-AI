package ai.project.governance.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import ai.project.governance.ui.screens.DashboardScreen
import ai.project.governance.ui.screens.IntentScreen
import ai.project.governance.ui.screens.AuditScreen
import ai.project.governance.ui.screens.TarlScreen

sealed class Screen(val route: String) {
    object Dashboard : Screen("dashboard")
    object Intent : Screen("intent")
    object Audit : Screen("audit")
    object Tarl : Screen("tarl")
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = Screen.Dashboard.route
    ) {
        composable(Screen.Dashboard.route) {
            DashboardScreen(navController = navController)
        }
        composable(Screen.Intent.route) {
            IntentScreen(navController = navController)
        }
        composable(Screen.Audit.route) {
            AuditScreen(navController = navController)
        }
        composable(Screen.Tarl.route) {
            TarlScreen(navController = navController)
        }
    }
}
