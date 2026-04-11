// Package anomaly — mahalanobis_test.go
//
// Unit tests for Mahalanobis distance computation and matrix operations.
// Target: 100% coverage of all matrix math paths.

package anomaly

import (
	"math"
	"testing"
)

func TestMahalanobisSquared_Identity(t *testing.T) {
	// Identity covariance → Mahalanobis = Euclidean
	v := []float64{1.0, 2.0, 3.0}
	M := [][]float64{
		{1.0, 0.0, 0.0},
		{0.0, 1.0, 0.0},
		{0.0, 0.0, 1.0},
	}
	
	got := MahalanobisSquared(v, M)
	expected := 1.0*1.0 + 2.0*2.0 + 3.0*3.0 // 14.0
	
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("MahalanobisSquared(%v, I) = %v, want %v", v, got, expected)
	}
}

func TestMahalanobisSquared_ScaledIdentity(t *testing.T) {
	// M = 2*I → Mahalanobis^2 = 2 * Euclidean^2
	v := []float64{1.0, 0.0}
	M := [][]float64{
		{2.0, 0.0},
		{0.0, 2.0},
	}
	
	got := MahalanobisSquared(v, M)
	expected := 2.0 * (1.0*1.0) // 2.0
	
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("MahalanobisSquared(%v, 2I) = %v, want %v", v, got, expected)
	}
}

func TestMahalanobisSquared_NonDiagonal(t *testing.T) {
	// Test with correlation
	v := []float64{1.0, 1.0}
	M := [][]float64{
		{2.0, 1.0},
		{1.0, 2.0},
	}
	
	// Mv = [[2,1],[1,2]] * [1,1] = [3, 3]
	// v·Mv = [1,1]·[3,3] = 6
	got := MahalanobisSquared(v, M)
	expected := 6.0
	
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("MahalanobisSquared(%v, M) = %v, want %v", v, got, expected)
	}
}

// Helper to create function pointer for testing
func MahalanobisSquared(v []float64, M [][]float64) float64 {
	return mahalanobisSquared(v, M)
}

func TestEuclideanSquared_Zero(t *testing.T) {
	v := []float64{0.0, 0.0, 0.0}
	got := euclideanSquared(v)
	if got != 0.0 {
		t.Errorf("euclideanSquared([0,0,0]) = %v, want 0.0", got)
	}
}

func TestEuclideanSquared_Unit(t *testing.T) {
	v := []float64{1.0, 0.0, 0.0}
	got := euclideanSquared(v)
	if math.Abs(got-1.0) > 1e-9 {
		t.Errorf("euclideanSquared([1,0,0]) = %v, want 1.0", got)
	}
}

func TestEuclideanSquared_Pythagorean(t *testing.T) {
	v := []float64{3.0, 4.0}
	got := euclideanSquared(v)
	expected := 25.0
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("euclideanSquared([3,4]) = %v, want %v", v, got, expected)
	}
}

func TestInvertCovariance_Identity(t *testing.T) {
	cov := [][]float64{
		{1.0, 0.0, 0.0},
		{0.0, 1.0, 0.0},
		{0.0, 0.0, 1.0},
	}
	
	inv := InvertCovariance(cov)
	if inv == nil {
		t.Fatal("InvertCovariance(I) returned nil")
	}
	
	// Verify I^-1 = I
	for i := 0; i < 3; i++ {
		for j := 0; j < 3; j++ {
			expected := 0.0
			if i == j {
				expected = 1.0
			}
			if math.Abs(inv[i][j]-expected) > 1e-9 {
				t.Errorf("inv[%d][%d] = %v, want %v", i, j, inv[i][j], expected)
			}
		}
	}
}

func TestInvertCovariance_Diagonal(t *testing.T) {
	cov := [][]float64{
		{4.0, 0.0},
		{0.0, 9.0},
	}
	
	inv := InvertCovariance(cov)
	if inv == nil {
		t.Fatal("InvertCovariance(diag) returned nil")
	}
	
	// Inverse of diagonal: 1/diagonal
	expected := [][]float64{
		{0.25, 0.0},
		{0.0, 1.0 / 9.0},
	}
	
	for i := 0; i < 2; i++ {
		for j := 0; j < 2; j++ {
			if math.Abs(inv[i][j]-expected[i][j]) > 1e-9 {
				t.Errorf("inv[%d][%d] = %v, want %v", i, j, inv[i][j], expected[i][j])
			}
		}
	}
}

func TestInvertCovariance_Singular(t *testing.T) {
	// Singular matrix (all zeros)
	cov := [][]float64{
		{0.0, 0.0},
		{0.0, 0.0},
	}
	
	inv := InvertCovariance(cov)
	if inv != nil {
		t.Errorf("InvertCovariance(singular) = %v, want nil", inv)
	}
}

func TestInvertCovariance_NotPositiveDefinite(t *testing.T) {
	// Negative eigenvalue (not positive-definite)
	cov := [][]float64{
		{1.0, 2.0},
		{2.0, 1.0},
	}
	// Eigenvalues: 3 and -1 → not positive-definite
	
	inv := InvertCovariance(cov)
	if inv != nil {
		t.Errorf("InvertCovariance(not PD) = %v, want nil", inv)
	}
}

func TestInvertCovariance_2x2(t *testing.T) {
	// Standard 2×2 positive-definite matrix
	cov := [][]float64{
		{2.0, 1.0},
		{1.0, 2.0},
	}
	
	inv := InvertCovariance(cov)
	if inv == nil {
		t.Fatal("InvertCovariance returned nil for valid matrix")
	}
	
	// Expected inverse: (1/3) * [[2, -1], [-1, 2]]
	expected := [][]float64{
		{2.0 / 3.0, -1.0 / 3.0},
		{-1.0 / 3.0, 2.0 / 3.0},
	}
	
	for i := 0; i < 2; i++ {
		for j := 0; j < 2; j++ {
			if math.Abs(inv[i][j]-expected[i][j]) > 1e-9 {
				t.Errorf("inv[%d][%d] = %v, want %v", i, j, inv[i][j], expected[i][j])
			}
		}
	}
}

func TestCholeskyDecompose_Identity(t *testing.T) {
	A := [][]float64{
		{1.0, 0.0},
		{0.0, 1.0},
	}
	
	L := choleskyDecompose(A)
	if L == nil {
		t.Fatal("choleskyDecompose(I) returned nil")
	}
	
	// L should also be I
	for i := 0; i < 2; i++ {
		for j := 0; j < 2; j++ {
			expected := 0.0
			if i == j {
				expected = 1.0
			}
			if math.Abs(L[i][j]-expected) > 1e-9 {
				t.Errorf("L[%d][%d] = %v, want %v", i, j, L[i][j], expected)
			}
		}
	}
}

func TestCholeskyDecompose_NotPD(t *testing.T) {
	// Not positive-definite
	A := [][]float64{
		{-1.0, 0.0},
		{0.0, 1.0},
	}
	
	L := choleskyDecompose(A)
	if L != nil {
		t.Errorf("choleskyDecompose(not PD) = %v, want nil", L)
	}
}

func TestInvertLowerTriangular_Identity(t *testing.T) {
	L := [][]float64{
		{1.0, 0.0},
		{0.0, 1.0},
	}
	
	inv := invertLowerTriangular(L)
	if inv == nil {
		t.Fatal("invertLowerTriangular(I) returned nil")
	}
	
	for i := 0; i < 2; i++ {
		for j := 0; j < 2; j++ {
			expected := 0.0
			if i == j {
				expected = 1.0
			}
			if math.Abs(inv[i][j]-expected) > 1e-9 {
				t.Errorf("inv[%d][%d] = %v, want %v", i, j, inv[i][j], expected)
			}
		}
	}
}

func TestInvertLowerTriangular_Singular(t *testing.T) {
	L := [][]float64{
		{0.0, 0.0},
		{1.0, 0.0},
	}
	
	inv := invertLowerTriangular(L)
	if inv != nil {
		t.Errorf("invertLowerTriangular(singular) = %v, want nil", inv)
	}
}

func BenchmarkMahalanobisSquared(b *testing.B) {
	v := []float64{1.0, 2.0, 3.0}
	M := [][]float64{
		{2.0, 1.0, 0.0},
		{1.0, 3.0, 1.0},
		{0.0, 1.0, 2.0},
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = mahalanobisSquared(v, M)
	}
}

func BenchmarkInvertCovariance(b *testing.B) {
	cov := [][]float64{
		{2.0, 1.0, 0.5},
		{1.0, 3.0, 1.0},
		{0.5, 1.0, 2.0},
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = InvertCovariance(cov)
	}
}
