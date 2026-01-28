package ai.project.governance.data.repository

import ai.project.governance.data.api.GovernanceApi
import ai.project.governance.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

sealed class Resource<T> {
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String) : Resource<T>()
    class Loading<T> : Resource<T>()
}

@Singleton
class GovernanceRepository @Inject constructor(
    private val api: GovernanceApi
) {
    
    fun getHealth(): Flow<Resource<HealthResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = api.getHealth()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch health: ${response.message()}"))
            }
        } catch (e: Exception) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        }
    }
    
    fun getTarl(): Flow<Resource<TarlResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = api.getTarl()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch TARL: ${response.message()}"))
            }
        } catch (e: Exception) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        }
    }
    
    fun getAudit(limit: Int = 50): Flow<Resource<AuditResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = api.getAudit(limit)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch audit: ${response.message()}"))
            }
        } catch (e: Exception) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        }
    }
    
    fun submitIntent(intent: Intent): Flow<Resource<IntentResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = api.submitIntent(intent)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                val errorBody = response.errorBody()?.string()
                emit(Resource.Error("Governance denied: $errorBody"))
            }
        } catch (e: Exception) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        }
    }
    
    fun execute(intent: Intent): Flow<Resource<ExecuteResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = api.execute(intent)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                val errorBody = response.errorBody()?.string()
                emit(Resource.Error("Execution denied: $errorBody"))
            }
        } catch (e: Exception) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        }
    }
}
