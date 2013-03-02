//
//  ECUploadManager.h
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface ECUploadManager : NSObject

@property (retain) NSString* cacheDirectory;
@property (retain) NSDate* lastValidCache;
@property dispatch_queue_t uploadQueue;

- (id)init;

/**
 * Locate a cache directory from a EVE Mac install
 */
- (void)locateCacheDirectory;


/**
 * Process a known cache filename for market orders
 */
- (void) scanFile:(NSString*) name;

/**
 * Scan files in the cache directory and schedule uploads.
 */
- (void) scan;

@end
