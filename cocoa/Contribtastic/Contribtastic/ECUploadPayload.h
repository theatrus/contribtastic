//
//  ECUploadPayload.h
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface ECUploadPayload : NSObject

@property (assign) NSMutableDictionary *payloadDict;

- (id) init;

- (NSMutableDictionary*) buildPreamble;

@end
