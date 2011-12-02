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
- (void)locateCacheDirectory;
- (void) scanFile:(NSString*) name;
- (void) scan;

@end
