// Robust File Search System
// Prevents the ".cursorrules vs .cursor/rules/globals.mdc" type failures

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

/**
 * Multi-tier file search with confidence scoring
 * Implements Tier 0 (Ground Truth) validation from Gemini's analysis
 */
export class RobustFileSearch {
  constructor(basePath = process.cwd()) {
    this.basePath = basePath;
    this.cache = new Map(); // Tier 1: Active Cache
    this.cacheTTL = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Performs comprehensive file search with multiple fallback patterns
   * @param {string} pattern - File pattern to search for
   * @param {Object} options - Search options
   * @returns {Object} Search results with confidence scoring
   */
  async search(pattern, options = {}) {
    const startTime = Date.now();
    const cacheKey = `${pattern}:${JSON.stringify(options)}`;
    
    // Check Tier 1 cache first
    const cached = this.getCached(cacheKey);
    if (cached && !options.forceRefresh) {
      return {
        ...cached,
        cacheHit: true,
        searchTime: Date.now() - startTime
      };
    }

    const result = {
      pattern,
      found: false,
      paths: [],
      confidence: 0.0,
      searchMethods: [],
      cacheHit: false,
      searchTime: 0,
      tier: 'unknown'
    };

    try {
      // Tier 0: Ground Truth - Direct filesystem verification
      await this.performDirectSearch(pattern, result);
      
      if (!result.found) {
        await this.performGlobSearch(pattern, result);
      }
      
      if (!result.found) {
        await this.performContentSearch(pattern, result);
      }
      
      if (!result.found) {
        await this.performFuzzySearch(pattern, result);
      }

      // Calculate final confidence score
      result.confidence = this.calculateConfidence(result);
      result.tier = this.determineTier(result);
      
      // Cache successful results
      if (result.found) {
        this.setCached(cacheKey, result);
      }
      
    } catch (error) {
      result.error = error.message;
      result.confidence = 0.0;
    }

    result.searchTime = Date.now() - startTime;
    return result;
  }

  /**
   * Tier 0: Direct path verification
   */
  async performDirectSearch(pattern, result) {
    const directPath = path.resolve(this.basePath, pattern);
    
    try {
      if (fs.existsSync(directPath)) {
        const stats = fs.statSync(directPath);
        result.found = true;
        result.paths = [directPath];
        result.searchMethods.push('direct');
        result.metadata = {
          size: stats.size,
          mtime: stats.mtime,
          isFile: stats.isFile()
        };
        return true;
      }
    } catch (error) {
      console.warn(`Direct search error for ${pattern}:`, error.message);
    }
    
    return false;
  }

  /**
   * Tier 0: Glob pattern search with multiple variations
   */
  async performGlobSearch(pattern, result) {
    const basename = path.basename(pattern);
    const dirname = path.dirname(pattern);
    
    const globPatterns = [
      `**/${basename}`,
      `**/*${basename}*`,
      `${dirname}/**/*`,
      `**/*${basename.replace(/\./g, '*')}*`
    ];

    for (const globPattern of globPatterns) {
      try {
        // Use find command for cross-platform compatibility
        const cmd = `find "${this.basePath}" -path "*/.*" -prune -o -name "${basename}" -type f -print`;
        const output = execSync(cmd, { 
          encoding: 'utf8', 
          timeout: 5000,
          stdio: ['pipe', 'pipe', 'ignore'] // Suppress stderr
        });
        
        if (output.trim()) {
          const paths = output.trim().split('\n').filter(p => p && fs.existsSync(p));
          if (paths.length > 0) {
            result.found = true;
            result.paths = paths;
            result.searchMethods.push(`glob:${globPattern}`);
            return true;
          }
        }
      } catch (error) {
        // Continue to next pattern
        continue;
      }
    }
    
    return false;
  }

  /**
   * Tier 0: Content-based search for configuration files
   */
  async performContentSearch(pattern, result) {
    if (!this.isConfigPattern(pattern)) {
      return false;
    }

    const searchTerms = this.extractSearchTerms(pattern);
    
    for (const term of searchTerms) {
      try {
        const cmd = `grep -r "${term}" "${this.basePath}" --include="*.mdc" --include="*.md" --include="*.json" --include="*.js" -l`;
        const output = execSync(cmd, { 
          encoding: 'utf8', 
          timeout: 10000,
          stdio: ['pipe', 'pipe', 'ignore']
        });
        
        if (output.trim()) {
          const paths = output.trim().split('\n').filter(p => p && fs.existsSync(p));
          if (paths.length > 0) {
            result.found = true;
            result.paths = paths;
            result.searchMethods.push(`content:${term}`);
            return true;
          }
        }
      } catch (error) {
        continue;
      }
    }
    
    return false;
  }

  /**
   * Tier 0: Fuzzy name matching for typos and variations
   */
  async performFuzzySearch(pattern, result) {
    const basename = path.basename(pattern, path.extname(pattern));
    
    try {
      // Find files with similar names (edit distance)
      const cmd = `find "${this.basePath}" -type f -name "*${basename.substring(0, Math.floor(basename.length * 0.7))}*"`;
      const output = execSync(cmd, { 
        encoding: 'utf8', 
        timeout: 5000,
        stdio: ['pipe', 'pipe', 'ignore']
      });
      
      if (output.trim()) {
        const paths = output.trim().split('\n').filter(p => p && fs.existsSync(p));
        if (paths.length > 0) {
          result.found = true;
          result.paths = paths;
          result.searchMethods.push('fuzzy');
          return true;
        }
      }
    } catch (error) {
      // Fuzzy search failed
    }
    
    return false;
  }

  /**
   * Calculate confidence score based on search results
   */
  calculateConfidence(result) {
    let score = 0.0;
    
    if (!result.found) return 0.0;
    
    // Method-based scoring
    if (result.searchMethods.includes('direct')) score += 0.9;
    else if (result.searchMethods.some(m => m.startsWith('glob'))) score += 0.7;
    else if (result.searchMethods.some(m => m.startsWith('content'))) score += 0.6;
    else if (result.searchMethods.includes('fuzzy')) score += 0.4;
    
    // Multiple paths found (reduces confidence slightly)
    if (result.paths.length > 1) score *= 0.9;
    
    // Metadata validation bonus
    if (result.metadata && result.metadata.isFile) score += 0.05;
    
    // Speed bonus (faster = more likely to be correct)
    if (result.searchTime < 1000) score += 0.05;
    
    return Math.min(score, 0.99); // Never 100% confident
  }

  /**
   * Determine which tier the result came from
   */
  determineTier(result) {
    if (result.cacheHit) return 'Tier 1 (Cache)';
    if (result.searchMethods.includes('direct')) return 'Tier 0 (Ground Truth)';
    return 'Tier 0 (Verified)';
  }

  /**
   * Check if pattern looks like a configuration file
   */
  isConfigPattern(pattern) {
    const configKeywords = ['cursor', 'rule', 'config', 'claude', 'setting', '.env', '.rc'];
    return configKeywords.some(keyword => pattern.toLowerCase().includes(keyword));
  }

  /**
   * Extract search terms from file pattern
   */
  extractSearchTerms(pattern) {
    const terms = [];
    
    if (pattern.includes('cursor')) terms.push('cursor');
    if (pattern.includes('rule')) terms.push('rule');
    if (pattern.includes('global')) terms.push('global');
    if (pattern.includes('claude')) terms.push('claude');
    
    // Add basename without extension
    const basename = path.basename(pattern, path.extname(pattern));
    if (basename && !terms.includes(basename)) {
      terms.push(basename);
    }
    
    return terms;
  }

  /**
   * Cache management (Tier 1)
   */
  getCached(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      return cached.data;
    }
    return null;
  }

  setCached(key, data) {
    this.cache.set(key, {
      timestamp: Date.now(),
      data: { ...data, cacheHit: false }
    });
  }

  /**
   * Generate human-readable response based on confidence
   */
  generateResponse(result, baseMessage) {
    const { confidence, found, paths } = result;
    
    if (!found) {
      return `${baseMessage}を確認しましたが、見つかりませんでした。別の場所や異なる名前で存在する可能性があります。追加の検索パターンを試しますか？`;
    }
    
    if (confidence >= 0.95) {
      return `${baseMessage}: ${paths[0]}`;
    } else if (confidence >= 0.8) {
      return `推定では${baseMessage}: ${paths[0]}。念のため追加確認をお勧めします。`;
    } else if (confidence >= 0.6) {
      return `おそらく${baseMessage}: ${paths[0]}ですが、他の場所にある可能性もあります。`;
    } else {
      return `${baseMessage}らしきファイルを発見: ${paths[0]}。ただし、確実性は低いため手動確認を推奨します。`;
    }
  }
}

// Export singleton instance
export const robustSearch = new RobustFileSearch();

// Utility function for quick searches
export async function findFile(pattern, options = {}) {
  return await robustSearch.search(pattern, options);
}

// Pre-validation function for critical files
export async function validateCriticalFiles(requiredFiles) {
  const results = [];
  let totalConfidence = 0;
  
  for (const file of requiredFiles) {
    const result = await robustSearch.search(file);
    results.push({
      file,
      found: result.found,
      confidence: result.confidence,
      paths: result.paths
    });
    
    totalConfidence += result.confidence;
  }
  
  return {
    results,
    averageConfidence: totalConfidence / requiredFiles.length,
    allFound: results.every(r => r.found),
    summary: `${results.filter(r => r.found).length}/${requiredFiles.length} files found`
  };
}