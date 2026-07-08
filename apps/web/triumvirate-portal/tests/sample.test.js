/**
 * Sample Jest Test File
 * This demonstrates basic Jest testing structure for The Triumvirate project
 */

describe('The Triumvirate - Sample Tests', () => {
  describe('Basic Math Operations', () => {
    test('addition works correctly', () => {
      expect(1 + 1).toBe(2);
      expect(2 + 2).toBe(4);
    });

    test('subtraction works correctly', () => {
      expect(5 - 3).toBe(2);
      expect(10 - 7).toBe(3);
    });
  });

  describe('String Operations', () => {
    test('string concatenation works', () => {
      const str1 = 'The';
      const str2 = 'Triumvirate';
      expect(str1 + ' ' + str2).toBe('The Triumvirate');
    });

    test('string includes method works', () => {
      const projectName = 'The Triumvirate: AI × Humanity × Technology';
      expect(projectName).toContain('Triumvirate');
      expect(projectName).toContain('AI');
      expect(projectName).toContain('Humanity');
      expect(projectName).toContain('Technology');
    });
  });

  describe('Array Operations', () => {
    test('array contains expected elements', () => {
      const triumvirate = ['Project AI', 'Cerberus', 'Codex Deus Maximus'];
      expect(triumvirate).toHaveLength(3);
      expect(triumvirate).toContain('Project AI');
      expect(triumvirate).toContain('Cerberus');
      expect(triumvirate).toContain('Codex Deus Maximus');
    });

    test('array mapping works correctly', () => {
      const numbers = [1, 2, 3, 4];
      const doubled = numbers.map(n => n * 2);
      expect(doubled).toEqual([2, 4, 6, 8]);
    });
  });

  describe('Object Operations', () => {
    test('object properties are accessible', () => {
      const project = {
        name: 'The Triumvirate',
        version: '1.0.0',
        components: 3
      };
      
      expect(project.name).toBe('The Triumvirate');
      expect(project.version).toBe('1.0.0');
      expect(project.components).toBe(3);
    });

    test('object methods work correctly', () => {
      const calculator = {
        value: 0,
        add(n) {
          this.value += n;
          return this;
        },
        getValue() {
          return this.value;
        }
      };

      calculator.add(5).add(3);
      expect(calculator.getValue()).toBe(8);
    });
  });
});
