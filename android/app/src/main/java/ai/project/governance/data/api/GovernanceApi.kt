package ai.project.governance.data.api

import ai.project.governance.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface GovernanceApi {
    
    @GET("health")
    suspend fun getHealth(): Response<HealthResponse>
    
    @GET("tarl")
    suspend fun getTarl(): Response<TarlResponse>
    
    @GET("audit")
    suspend fun getAudit(
        @Query("limit") limit: Int = 50
    ): Response<AuditResponse>
    
    @POST("intent")
    suspend fun submitIntent(
        @Body intent: Intent
    ): Response<IntentResponse>
    
    @POST("execute")
    suspend fun execute(
        @Body intent: Intent
    ): Response<ExecuteResponse>
}
